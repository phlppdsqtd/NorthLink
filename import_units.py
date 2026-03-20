import os
import django
import csv
from datetime import datetime

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from properties.models import Building, Unit
from tenants.models import TenantProfile
from django.contrib.auth.models import User

def parse_date(date_str):
    """Converts CSV date (25 11 2025) to Django DB date (2025-11-25)"""
    if not date_str:
        return None
    try:
        # Changed to %d %m %Y to match the spaces in your CSV
        return datetime.strptime(date_str.strip(), '%d %m %Y').date()
    except ValueError:
        return None

def import_data():
    file_path = 'units_rows.csv'
    if not os.path.exists(file_path):
        print(f"Error: Could not find {file_path}")
        return

    print("--- Starting Clean Data Import ---")

    with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0
        
        for row in reader:
            # --- 1. PHYSICAL PROPERTY ---
            b_name = row['building'].strip()
            building, _ = Building.objects.get_or_create(name=b_name)

            unit_code = row['unit_code'].strip().upper()
            unit, _ = Unit.objects.get_or_create(unit_code=unit_code, building=building)
            
            # Map Unit Details
            unit.unit_type = row.get('unit_type', '').strip()
            unit.capacity = int(row['capacity']) if row.get('capacity') else 0
            unit.occupancy = int(row['occupancy']) if row.get('occupancy') else 0
            unit.room_size = row.get('room_size', '').strip()
            unit.furnish = row.get('furnish', '').strip()
            unit.restroom = row.get('restroom', '').strip()
            unit.curfew = row.get('curfew', '').strip()
            unit.monthly_rent = float(row['price_lease']) if row.get('price_lease') else 0.00
            unit.status = row.get('status', 'Available').strip().capitalize()
            unit.save()

            # --- 2. TENANT & LOGIN ---
            fname = row.get('first_name', '').strip()
            lname = row.get('last_name', '').strip()

            # If there is a tenant name in the row, create a User and Profile
            if fname or lname:
                # We use the unit_code (e.g., NG202) as the username so it's easy to log in
                user, user_created = User.objects.get_or_create(username=unit_code)
                
                if user_created:
                    user.set_password('tenant123') # Default password
                
                user.first_name = fname
                user.last_name = lname
                user.save()

                # Link the User to the physical Unit via the TenantProfile
                profile, _ = TenantProfile.objects.get_or_create(user=user)
                profile.unit = unit
                profile.contact_number = row.get('contact', '').strip()
                profile.term_lease = int(row['term_lease']) if row.get('term_lease') else 0
                profile.lease_start = parse_date(row.get('start_lease', ''))
                profile.lease_end = parse_date(row.get('end_lease', ''))
                profile.save()

            count += 1
            print(f"[{count}] Processed: {unit_code}")

    print("\nSuccess! Database is securely populated.")

if __name__ == '__main__':
    import_data()