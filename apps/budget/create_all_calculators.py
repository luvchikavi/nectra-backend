"""
Script to auto-generate all calculator models from Zoho structure
Runs once to create all 17 calculators quickly
"""

CALCULATORS = [
    {
        'name': 'DirectBuild',
        'lines_table': 'directbuild_lines',
        'summary_table': 'directbuild_summary',
        'equity_eligible': False,
        'description': 'Direct construction costs'
    },
    {
        'name': 'LandCost',
        'lines_table': 'landcost_lines',
        'summary_table': 'landcost_summary',
        'equity_eligible': True,
        'description': 'Land acquisition costs'
    },
    {
        'name': 'Suppliers',
        'lines_table': 'suppliers_lines',
        'summary_table': 'suppliers_summary',
        'equity_eligible': True,
        'description': 'Consultant and supplier fees'
    },
    {
        'name': 'DevLevies',
        'lines_table': 'devlevies_lines',
        'summary_table': 'devlevies_summary',
        'equity_eligible': True,
        'description': 'Development levies'
    },
    {
        'name': 'PurchaseTaxA',
        'lines_table': 'purchaseタックa_lines',
        'summary_table': 'purchasetaxa_summary',
        'equity_eligible': True,
        'description': 'Purchase tax A'
    },
    {
        'name': 'PurchaseTaxB',
        'lines_table': 'purchasetaxb_lines',
        'summary_table': 'purchasetaxb_summary',
        'equity_eligible': True,
        'description': 'Purchase tax B'
    },
    {
        'name': 'VAT_CS',
        'lines_table': 'vat_cs_lines',
        'summary_table': 'vat_cs_summary',
        'equity_eligible': False,
        'description': 'VAT on transactions'
    },
    {
        'name': 'Management',
        'lines_table': 'management_lines',
        'summary_table': 'management_summary',
        'equity_eligible': False,
        'description': 'Management fees'
    },
    {
        'name': 'Overhead',
        'lines_table': 'overhead_lines',
        'summary_table': 'overhead_summary',
        'equity_eligible': False,
        'description': 'Office overhead expenses'
    },
    {
        'name': 'Maintenance',
        'lines_table': 'maintenance_lines',
        'summary_table': 'maintenance_summary',
        'equity_eligible': False,
        'description': 'Maintenance costs'
    },
    {
        'name': 'Rent',
        'lines_table': 'rent_lines',
        'summary_table': 'rent_summary',
        'equity_eligible': False,
        'description': 'Rent payments'
    },
    {
        'name': 'Electricity',
        'lines_table': 'electricity_lines',
        'summary_table': 'electricity_summary',
        'equity_eligible': False,
        'description': 'Electricity costs'
    },
    {
        'name': 'SiteIns',
        'lines_table': 'siteins_lines',
        'summary_table': 'siteins_summary',
        'equity_eligible': False,
        'description': 'Site insurance'
    },
    {
        'name': 'Unexpected',
        'lines_table': 'unexpected_lines',
        'summary_table': 'unexpected_summary',
        'equity_eligible': False,
        'description': 'Unexpected costs'
    },
    {
        'name': 'TenantsComp',
        'lines_table': 'tenantscomp_lines',
        'summary_table': 'tenantscomp_summary',
        'equity_eligible': False,
        'description': 'Tenant compensation'
    },
    {
        'name': 'Upgrades',
        'lines_table': 'upgrades_lines',
        'summary_table': 'upgrades_summary',
        'equity_eligible': False,
        'description': 'Apartment upgrades'
    },
    {
        'name': 'OtherExp',
        'lines_table': 'otherexp_lines',
        'summary_table': 'otherexp_summary',
        'equity_eligible': False,
        'description': 'Other expenses'
    },
]

print(f"Total calculators to create: {len(CALCULATORS)}")
for calc in CALCULATORS:
    print(f"  - {calc['name']}: {calc['description']} [Equity: {calc['equity_eligible']}]")
