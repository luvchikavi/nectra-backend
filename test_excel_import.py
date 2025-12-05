#!/usr/bin/env python
"""
Test script for Excel apartment import
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.projects.models import Project
from apps.sales.excel_importer import import_apartments_from_excel


def main():
    print("=" * 80)
    print("TESTING EXCEL APARTMENT IMPORTER")
    print("=" * 80)

    # Create a test project
    project, created = Project.objects.get_or_create(
        project_name="Test Import Project",
        defaults={
            'project_id': 'TEST-2025-0001'
        }
    )

    if created:
        print(f"\n✓ Created test project: {project}")
    else:
        print(f"\n✓ Using existing project: {project}")

    # Path to your Excel file
    excel_file = "/Users/aviluvchik/Downloads/Input Data_Nectra.xlsx"

    if not os.path.exists(excel_file):
        print(f"\n❌ ERROR: Excel file not found at: {excel_file}")
        print("Please make sure the file exists at this location.")
        return

    print(f"\n✓ Found Excel file: {excel_file}")
    print(f"\nStarting import...")
    print("-" * 80)

    # Import apartments
    results = import_apartments_from_excel(project, excel_file)

    # Display results
    print("\n" + "=" * 80)
    print("IMPORT RESULTS")
    print("=" * 80)
    print(f"\n✓ Successfully imported: {results['imported']} apartments")
    print(f"⚠  Skipped: {results['skipped']} rows")

    if results['warnings']:
        print(f"\n⚠  WARNINGS ({len(results['warnings'])}):")
        for warning in results['warnings']:
            print(f"   - {warning}")

    if results['errors']:
        print(f"\n❌ ERRORS ({len(results['errors'])}):")
        for error in results['errors'][:10]:  # Show first 10 errors
            print(f"   - {error}")
        if len(results['errors']) > 10:
            print(f"   ... and {len(results['errors']) - 10} more errors")

    # Show some sample data
    from apps.sales.models import ApartmentInventory

    apartments = ApartmentInventory.objects.filter(project=project)
    print(f"\n" + "=" * 80)
    print(f"IMPORTED APARTMENTS SUMMARY ({apartments.count()} total)")
    print("=" * 80)

    # Group by status
    statuses = apartments.values('unit_status').annotate(
        count=django.db.models.Count('id')
    ).order_by('-count')

    print("\nBy Status:")
    for status_group in statuses:
        status_display = dict(ApartmentInventory.UNIT_STATUS).get(
            status_group['unit_status'],
            status_group['unit_status']
        )
        print(f"  - {status_display}: {status_group['count']}")

    # Group by unit type
    types = apartments.values('unit_type').annotate(
        count=django.db.models.Count('id')
    ).order_by('-count')

    print("\nBy Unit Type:")
    for type_group in types:
        type_display = dict(ApartmentInventory.UNIT_TYPES).get(
            type_group['unit_type'],
            type_group['unit_type']
        )
        print(f"  - {type_display}: {type_group['count']}")

    # Show first 5 apartments
    print("\nFirst 5 Imported Apartments:")
    print("-" * 80)
    for apt in apartments[:5]:
        print(f"\n{apt.unit_unique_id}")
        print(f"  Building: {apt.building_number}, Floor: {apt.floor}, Unit: {apt.unit_number}")
        print(f"  Type: {apt.get_unit_type_display()}")
        print(f"  Rooms: {apt.room_count if apt.room_count else 'N/A'}")
        print(f"  Area: {apt.unit_area_sqm or apt.net_area_sqm} sqm")
        print(f"  Price: ₪{apt.list_price_with_vat:,.0f}" if apt.list_price_with_vat else "  Price: Not set")
        print(f"  Status: {apt.get_unit_status_display()}")
        if apt.customer_full_name:
            print(f"  Customer: {apt.customer_full_name}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == '__main__':
    main()
