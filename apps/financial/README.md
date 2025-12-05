# Financial Module

## 🎯 Purpose
The Financial module is the **HEART** of the Nectar system. It handles all financial tracking for Stage 7 projects (Financial Supervision phase, which lasts 27-30 months).

## ⚠️ CRITICAL IMPORTANCE
This module contains the **Monthly Balance Calculation** - the most important business logic in the entire system.

---

## 📁 Directory Structure

```
financial/
├── models/
│   ├── __init__.py
│   ├── cash_flow_transaction.py    # All money movements
│   ├── bank_account.py              # Project bank account tracking
│   ├── equity_tracking.py           # Monthly equity calculations
│   ├── equity_deposit.py            # Equity deposit records
│   ├── bank_approval.py             # Bank funding approvals
│   └── monthly_balance.py           # Monthly balance records (KEY TABLE)
├── services/
│   ├── __init__.py
│   ├── monthly_balance_service.py   # 🔴 CRITICAL: Monthly balance calculation
│   ├── equity_calculator.py         # Equity percentage calculations
│   ├── cash_flow_forecast.py        # 3-6 month forecast
│   └── bank_compliance.py           # Check bank requirements
├── serializers/
│   └── (API serializers)
├── views/
│   └── (API views)
├── tasks.py                         # Celery tasks
├── tests/
│   └── test_monthly_balance.py      # Critical tests
└── README.md (this file)
```

---

## 🔑 Key Features

### 1. Monthly Balance Calculation (CRITICAL)
**Runs:** 1st of every month at 9:00 AM (Celery Beat)

**Calculates:**
- Expected expenses for the month (from construction schedule)
- Expected income for the month (from payment schedules)
- Current bank account balance
- Required equity (based on bank agreement)
- Actual equity deposited
- Gap/Surplus (positive = surplus, negative = gap)
- Status (OK / WARNING / CRITICAL)
- Alerts if action needed

**File:** `services/monthly_balance_service.py`

### 2. Cash Flow Tracking
Tracks every money movement:
- Expenses (construction costs, supplier payments)
- Income (customer payments, sales)
- Equity deposits (owner investments)

**Model:** `models/cash_flow_transaction.py`

### 3. Equity Tracking
Monthly calculation of:
- Total project cost
- Bank financing amount
- Required equity percentage (e.g., 20%)
- Actual equity deposited
- Equity gap/surplus
- Compliance with bank requirements

**Model:** `models/equity_tracking.py`
**Service:** `services/equity_calculator.py`

### 4. Bank Account Management
Each project has a dedicated bank account that must be balanced:
- Account balance must cover: expenses + required equity - expected income
- Real-time balance tracking
- Alert system for low balance

**Model:** `models/bank_account.py`

### 5. Bank Approvals
Track funding requests to the bank:
- Request amount
- Supporting documents
- Approval status
- Transfer date

**Model:** `models/bank_approval.py`

---

## 📊 Database Schema

### CashFlowTransaction
```python
- id (PK)
- tenant_id (FK)              # Multi-tenancy
- project_id (FK)
- transaction_date
- amount
- transaction_type            # Expense / Income / Equity
- category
- description
- invoice_number
- supplier_id (FK, optional)
- apartment_id (FK, optional)
- budget_section_id (FK, optional)
- payment_method
- bank_account_id (FK)
- status                      # Pending / Approved / Rejected
- approved_by
- approved_date
- attachment
- created_at
- updated_at
```

### MonthlyBalance (KEY TABLE)
```python
- id (PK)
- tenant_id (FK)
- project_id (FK)
- month_year                  # e.g., "2025-11"
- calculation_date
- expected_expenses           # Calculated from construction schedule
- expected_income             # Calculated from payment schedules
- current_bank_balance        # From BankAccount
- required_equity             # From bank agreement
- actual_equity_deposited     # Sum of EquityDeposit
- gap_surplus                 # Positive = surplus, Negative = gap
- status                      # OK / WARNING / CRITICAL
- alerts (JSON)               # List of alerts
- created_at
- updated_at
```

### EquityTracking
```python
- id (PK)
- tenant_id (FK)
- project_id (FK)
- calculation_date
- total_project_cost          # From Budget
- bank_financing              # From financing agreement
- required_equity             # Calculated
- actual_equity_deposited     # Sum of deposits
- equity_gap                  # Required - Actual
- equity_percent              # Actual / Total * 100
- bank_requirement_percent    # e.g., 20%
- meets_requirement           # Boolean
- approved_by_bank
- approved_date
- notes
- created_at
- updated_at
```

---

## 🔧 Monthly Balance Service Logic

### High-Level Flow
```
1. Triggered on 1st of month (Celery Beat)
2. For each active Stage 7 project:
   a. Calculate expected expenses
   b. Calculate expected income
   c. Get current bank balance
   d. Calculate required equity
   e. Get actual equity deposited
   f. Calculate gap/surplus
   g. Determine status
   h. Generate alerts
   i. Save to MonthlyBalance table
   j. Send notifications if needed
```

### Expected Expenses Calculation
```python
Sources:
- Construction progress schedule (% complete per stage)
- Budget entries (costs per stage)
- Historical spending patterns
- Supplier payment schedules

Formula:
expected_expenses = sum of (
    planned_construction_this_month +
    scheduled_supplier_payments +
    overhead_costs
)
```

### Expected Income Calculation
```python
Sources:
- Customer payment schedules (payments due this month)
- Sales forecast (expected new sales)
- Contract terms (milestone payments)

Formula:
expected_income = sum of (
    scheduled_customer_payments_this_month +
    expected_milestone_payments +
    expected_new_sales_deposits
)
```

### Required Equity Calculation
```python
Formula:
required_equity = total_project_cost * bank_requirement_percent - bank_financing

Example:
- Total project cost: ₪10,000,000
- Bank financing: ₪8,000,000
- Bank requirement: 20% equity
- Required equity: ₪10,000,000 * 20% = ₪2,000,000
```

### Gap/Surplus Calculation
```python
Formula:
gap_surplus = (current_balance + expected_income) - (expected_expenses + required_equity)

Status determination:
- gap_surplus >= 0: OK
- -₪100K < gap_surplus < 0: WARNING
- gap_surplus <= -₪100K: CRITICAL
```

---

## 🚨 Alert System

### Alert Types
1. **Insufficient Balance** - Bank account will be negative
2. **Equity Gap** - Not enough equity deposited
3. **High Expenses** - Expenses exceed budget by >10%
4. **Low Income** - Income below forecast by >10%
5. **Bank Compliance** - Not meeting bank requirements

### Alert Generation Logic
```python
def generate_alerts(gap_surplus, actual_equity, required_equity):
    alerts = []
    
    if gap_surplus < 0:
        alerts.append({
            'type': 'INSUFFICIENT_BALANCE',
            'severity': 'CRITICAL' if gap_surplus < -100000 else 'WARNING',
            'message': f'Bank account will have deficit of ₪{abs(gap_surplus):,.0f}',
            'action': 'Request additional equity deposit or delay expenses'
        })
    
    if actual_equity < required_equity:
        gap = required_equity - actual_equity
        alerts.append({
            'type': 'EQUITY_GAP',
            'severity': 'CRITICAL',
            'message': f'Equity gap of ₪{gap:,.0f}',
            'action': f'Deposit additional ₪{gap:,.0f} to meet bank requirements'
        })
    
    return alerts
```

---

## 📡 API Endpoints

### Monthly Balance
```
GET    /api/v1/projects/{project_id}/monthly-balance/
       - Get monthly balance for all months
       
GET    /api/v1/projects/{project_id}/monthly-balance/latest/
       - Get latest monthly balance
       
GET    /api/v1/projects/{project_id}/monthly-balance/{month_year}/
       - Get balance for specific month
       
POST   /api/v1/projects/{project_id}/monthly-balance/calculate/
       - Manually trigger calculation (for testing)
```

### Cash Flow
```
GET    /api/v1/projects/{project_id}/cash-flow/
       - Get all transactions with filters
       
POST   /api/v1/projects/{project_id}/transactions/
       - Create new transaction
       
GET    /api/v1/projects/{project_id}/transactions/{id}/
       - Get transaction details
       
PATCH  /api/v1/projects/{project_id}/transactions/{id}/
       - Update transaction
       
DELETE /api/v1/projects/{project_id}/transactions/{id}/
       - Delete transaction
```

### Equity Tracking
```
GET    /api/v1/projects/{project_id}/equity-tracking/
       - Get equity tracking history
       
GET    /api/v1/projects/{project_id}/equity-tracking/latest/
       - Get latest equity status
       
POST   /api/v1/projects/{project_id}/equity-deposits/
       - Record new equity deposit
```

### Bank Approvals
```
GET    /api/v1/projects/{project_id}/bank-approvals/
       - Get all bank approval requests
       
POST   /api/v1/projects/{project_id}/bank-approvals/
       - Create new approval request
       
PATCH  /api/v1/projects/{project_id}/bank-approvals/{id}/
       - Update approval status
```

---

## 🧪 Testing

### Critical Tests
```python
# tests/test_monthly_balance.py

def test_monthly_balance_calculation_basic():
    """Test basic monthly balance calculation"""
    
def test_monthly_balance_with_surplus():
    """Test calculation when there's a surplus"""
    
def test_monthly_balance_with_deficit():
    """Test calculation when there's a deficit"""
    
def test_equity_gap_alert():
    """Test alert generation for equity gap"""
    
def test_insufficient_balance_alert():
    """Test alert generation for insufficient balance"""
    
def test_celery_task_execution():
    """Test that Celery task runs correctly"""
```

**All tests must pass before deployment!**

---

## 🔄 Celery Tasks

### Monthly Balance Calculation
```python
# tasks.py

@shared_task
def calculate_monthly_balance_all_projects():
    """
    Calculate monthly balance for all active Stage 7 projects
    Runs on 1st of every month at 9:00 AM
    """
    projects = Project.objects.filter(
        current_stage=7,
        status='ACTIVE'
    )
    
    for project in projects:
        try:
            service = MonthlyBalanceService()
            balance = service.calculate_monthly_balance(
                project_id=project.id,
                month_year=datetime.now().strftime('%Y-%m')
            )
            
            # Send notifications if alerts exist
            if balance.alerts:
                send_balance_alerts.delay(project.id, balance.id)
                
        except Exception as e:
            logger.error(f"Error calculating balance for project {project.id}: {e}")
```

### Equity Compliance Check
```python
@shared_task
def check_equity_compliance():
    """
    Check equity compliance for all active projects
    Runs every 6 hours
    """
    pass
```

---

## 🚀 Usage Examples

### Calculate Monthly Balance (Manual)
```python
from apps.financial.services.monthly_balance_service import MonthlyBalanceService

service = MonthlyBalanceService()
balance = service.calculate_monthly_balance(
    project_id=123,
    month_year='2025-11'
)

print(f"Expected Expenses: ₪{balance.expected_expenses:,.0f}")
print(f"Expected Income: ₪{balance.expected_income:,.0f}")
print(f"Gap/Surplus: ₪{balance.gap_surplus:,.0f}")
print(f"Status: {balance.status}")
print(f"Alerts: {balance.alerts}")
```

### Create Cash Flow Transaction
```python
from apps.financial.models import CashFlowTransaction

transaction = CashFlowTransaction.objects.create(
    project_id=123,
    transaction_date='2025-11-06',
    amount=250000,
    transaction_type='EXPENSE',
    category='CONSTRUCTION',
    description='Payment to main contractor',
    invoice_number='INV-2025-001',
    payment_method='BANK_TRANSFER'
)
```

---

## 📝 TODO / Future Enhancements

- [ ] Machine learning for expense prediction
- [ ] Real-time bank account integration
- [ ] Automated budget reallocation suggestions
- [ ] Multi-currency support
- [ ] Cash flow optimization algorithms
- [ ] Risk analysis and scoring

---

## ⚠️ CRITICAL NOTES

1. **NEVER skip monthly balance calculation** - it's the core of financial supervision
2. **ALWAYS validate data** before calculation - garbage in = garbage out
3. **ALERT immediately** if equity gap detected - bank compliance is critical
4. **TEST thoroughly** - financial calculations must be 100% accurate
5. **LOG everything** - audit trail is essential for banks

---

**Status:** ⬜ Not Started  
**Priority:** 🔴 CRITICAL  
**Owner:** To be assigned  
**Last Updated:** November 6, 2025
