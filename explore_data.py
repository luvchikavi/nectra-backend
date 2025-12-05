#!/usr/bin/env python
"""
Interactive data explorer for imported apartments
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.sales.models import ApartmentInventory, Customer, SalesTransaction
from apps.projects.models import Project
from decimal import Decimal


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def explore_apartments():
    """Explore apartment data"""
    print_section("📊 APARTMENT INVENTORY ANALYSIS")

    apartments = ApartmentInventory.objects.all()
    total = apartments.count()

    print(f"\n📈 Total Apartments: {total}")

    # Statistics by status
    print("\n🏷️  By Status:")
    for status_code, status_name in ApartmentInventory.UNIT_STATUS:
        count = apartments.filter(unit_status=status_code).count()
        if count > 0:
            percentage = (count / total * 100) if total > 0 else 0
            print(f"   {status_name:30} {count:3} units ({percentage:5.1f}%)")

    # Statistics by type
    print("\n🏠 By Unit Type:")
    for type_code, type_name in ApartmentInventory.UNIT_TYPES:
        count = apartments.filter(unit_type=type_code).count()
        if count > 0:
            percentage = (count / total * 100) if total > 0 else 0
            print(f"   {type_name:30} {count:3} units ({percentage:5.1f}%)")

    # Price statistics
    print("\n💰 Price Statistics:")
    apts_with_price = apartments.exclude(list_price_with_vat__isnull=True)
    if apts_with_price.exists():
        prices = [apt.list_price_with_vat for apt in apts_with_price]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)

        print(f"   Average Price: ₪{avg_price:,.0f}")
        print(f"   Min Price:     ₪{min_price:,.0f}")
        print(f"   Max Price:     ₪{max_price:,.0f}")
        print(f"   Total Value:   ₪{sum(prices):,.0f}")

    # Area statistics
    print("\n📐 Area Statistics:")
    apts_with_area = apartments.exclude(unit_area_sqm__isnull=True)
    if apts_with_area.exists():
        areas = [apt.unit_area_sqm for apt in apts_with_area]
        avg_area = sum(areas) / len(areas)
        min_area = min(areas)
        max_area = max(areas)

        print(f"   Average Area: {avg_area:.2f} sqm")
        print(f"   Min Area:     {min_area:.2f} sqm")
        print(f"   Max Area:     {max_area:.2f} sqm")

    # Buildings
    print("\n🏢 By Building:")
    buildings = apartments.values('building_number').distinct()
    for building in buildings:
        building_num = building['building_number']
        count = apartments.filter(building_number=building_num).count()
        print(f"   Building {building_num}: {count} units")


def show_sample_apartments():
    """Show detailed view of sample apartments"""
    print_section("🔍 SAMPLE APARTMENT DETAILS")

    apartments = ApartmentInventory.objects.all()[:5]

    for i, apt in enumerate(apartments, 1):
        print(f"\n{i}. {apt.unit_unique_id}")
        print(f"   {'─' * 70}")
        print(f"   Location:  Building {apt.building_number}, Floor {apt.floor}, Unit {apt.unit_number}")
        if apt.wing:
            print(f"   Wing:      {apt.wing}")
        print(f"   Type:      {apt.get_unit_type_display()}")
        if apt.unit_sub_type:
            print(f"   Sub-type:  {apt.unit_sub_type}")
        if apt.room_count:
            print(f"   Rooms:     {apt.room_count}")

        # Areas
        if apt.unit_area_sqm or apt.net_area_sqm:
            area = apt.unit_area_sqm or apt.net_area_sqm
            print(f"   Area:      {area} sqm")
        if apt.balcony_area_sqm:
            print(f"   Balcony:   {apt.balcony_area_sqm} sqm")
        if apt.terrace_area_sqm:
            print(f"   Terrace:   {apt.terrace_area_sqm} sqm")
        if apt.roof_terrace_area_sqm:
            print(f"   Roof:      {apt.roof_terrace_area_sqm} sqm")
        if apt.yard_area_sqm:
            print(f"   Yard:      {apt.yard_area_sqm} sqm")

        # Parking & Storage
        if apt.parking_spaces:
            print(f"   Parking:   {apt.parking_spaces} spots")
        if apt.storage_count:
            print(f"   Storage:   {apt.storage_count} units")

        # Pricing
        if apt.list_price_with_vat:
            print(f"   List Price: ₪{apt.list_price_with_vat:,.0f} (incl. VAT)")
            if apt.price_per_sqm_net_with_vat:
                print(f"   Price/sqm:  ₪{apt.price_per_sqm_net_with_vat:,.0f}")
        if apt.discount_percent > 0:
            print(f"   Discount:   {apt.discount_percent}%")
        if apt.final_price_with_vat:
            print(f"   Final:      ₪{apt.final_price_with_vat:,.0f}")

        # Status & Customer
        print(f"   Status:    {apt.get_unit_status_display()}")
        if apt.customer_full_name:
            print(f"   Customer:  {apt.customer_full_name}")


def query_examples():
    """Show example queries"""
    print_section("📝 EXAMPLE QUERIES")

    print("\n1️⃣  Find all FOR SALE apartments:")
    for_sale = ApartmentInventory.objects.filter(unit_status='FOR_SALE').count()
    print(f"   Result: {for_sale} apartments")

    print("\n2️⃣  Find apartments with 4+ rooms:")
    large_apts = ApartmentInventory.objects.filter(room_count__gte=4).count()
    print(f"   Result: {large_apts} apartments")

    print("\n3️⃣  Find most expensive apartment:")
    expensive = ApartmentInventory.objects.exclude(
        list_price_with_vat__isnull=True
    ).order_by('-list_price_with_vat').first()
    if expensive:
        print(f"   Result: {expensive.unit_unique_id}")
        print(f"   Price: ₪{expensive.list_price_with_vat:,.0f}")
        print(f"   Type: {expensive.get_unit_type_display()}")

    print("\n4️⃣  Find apartments with parking:")
    with_parking = ApartmentInventory.objects.filter(parking_spaces__gt=0).count()
    print(f"   Result: {with_parking} apartments")

    print("\n5️⃣  Find compensation units (תמורה):")
    compensation = ApartmentInventory.objects.filter(unit_status='COMPENSATION')
    print(f"   Result: {compensation.count()} apartments")
    for apt in compensation:
        print(f"   - {apt.unit_unique_id}: {apt.customer_full_name}")

    print("\n6️⃣  Calculate total inventory value:")
    total_value = sum(
        apt.list_price_with_vat or Decimal('0')
        for apt in ApartmentInventory.objects.all()
    )
    print(f"   Result: ₪{total_value:,.0f}")


def main():
    """Main function"""
    print("\n" + "🏢" * 40)
    print("\n   NECTAR - APARTMENT INVENTORY DATA EXPLORER")
    print("\n" + "🏢" * 40)

    # Show all analyses
    explore_apartments()
    show_sample_apartments()
    query_examples()

    print_section("✅ EXPLORATION COMPLETE")
    print("\n💡 TIP: Start Django server to explore in admin interface:")
    print("   cd backend")
    print("   source ../venv/bin/activate")
    print("   DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver")
    print("\n   Then visit: http://localhost:8000/admin")
    print("   Login with: admin / admin123")
    print("\n")


if __name__ == '__main__':
    main()
