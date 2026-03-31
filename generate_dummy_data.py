import os
import django
import random
from datetime import timedelta

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
# Adjust the import paths if your apps are named differently
from properties.models import Unit, Inquiry 
from tenants.models import TenantProfile
from billing.models import Bill
from maintenance.models import MaintenanceRequest

def backdate_model(model_class, obj_id, field_name, past_date):
    """
    Helper to bypass Django's auto_now_add=True which blocks manual date setting.
    Uses .update() directly on the database to force the date change.
    """
    model_class.objects.filter(id=obj_id).update(**{field_name: past_date})

def generate_dummy_data():
    print("--- Starting Dummy Data Generation ---")
    
    tenants = list(TenantProfile.objects.select_related('unit').all())
    units = list(Unit.objects.all())
    
    if not tenants or not units:
        print("Error: No tenants or units found! Please run your import_units.py first.")
        return

    now = timezone.now()
    
    # ==========================================
    # 1. GENERATE INQUIRIES
    # ==========================================
    print("Generating Inquiries...")
    inquiry_data = [
        {"name": "Mark Santos", "phone": "09171234567", "message": "Looking for a single room next month.", "resolved": False},
        {"name": "Sarah Lee", "phone": "09181234567", "message": "Do you have units with a private restroom?", "resolved": True},
        {"name": "John Doe", "phone": "09191234567", "message": "Is there a curfew for the building?", "resolved": False},
        {"name": "Maria Garcia", "phone": "09201234567", "message": "Interested in a bedspace starting next week.", "resolved": True},
        {"name": "Peter Lim", "phone": "09211234567", "message": "Can I schedule a viewing this Saturday?", "resolved": False}
    ]
    
    for i_data in inquiry_data:
        # Pick a random unit to inquire about
        random_unit = random.choice(units)
        
        # Random date within the last 30 days
        days_ago = random.randint(1, 30)
        fake_date = now - timedelta(days=days_ago)
        
        inquiry = Inquiry.objects.create(
            unit=random_unit,
            prospect_name=i_data["name"],
            contact_number=i_data["phone"],
            message=i_data["message"],
            is_resolved=i_data["resolved"]
        )
        backdate_model(Inquiry, inquiry.id, 'created_at', fake_date)

    # ==========================================
    # 2. GENERATE BILLS
    # ==========================================
    print("Generating Bills...")
    # Exact match to your models.py BILL_TYPES
    bill_types = ['rent', 'electricity', 'water'] 
    
    for tenant in tenants:
        if not tenant.unit:
            continue
            
        # Let's generate 2-4 random bills per tenant to give good dashboard data
        num_bills = random.randint(2, 4)
        
        for _ in range(num_bills):
            b_type = random.choice(bill_types)
            
            # Make Rent match their actual unit rent exactly
            if b_type == 'rent':
                amount = tenant.unit.monthly_rent
            elif b_type == 'electricity':
                amount = random.uniform(800, 2500)
            else: # water
                amount = random.uniform(150, 600)

            # Randomize paid/unpaid status
            status = random.choices(['paid', 'unpaid'], weights=[0.6, 0.4])[0]
            
            # Random past dates for due_date
            days_ago_due = random.randint(1, 60)
            due_date = (now - timedelta(days=days_ago_due)).date()
            
            bill = Bill.objects.create(
                tenant=tenant,
                bill_type=b_type,
                amount=round(amount, 2),
                status=status,
                due_date=due_date
            )
            
            # Backdate the created_at so your dashboard "Monthly Revenue" looks realistic
            # We assume the bill was created a few days before the due date
            created_date = now - timedelta(days=days_ago_due + 5) 
            backdate_model(Bill, bill.id, 'created_at', created_date)

    # ==========================================
    # 3. GENERATE MAINTENANCE REQUESTS
    # ==========================================
    print("Generating Maintenance Requests...")
    maintenance_issues = [
        "Leaking faucet in the bathroom",
        "Aircon not cooling properly",
        "Broken door lock",
        "Flickering lights in the hallway",
        "Clogged shower drain",
        "Window latch is broken",
        "Toilet won't flush"
    ]
    
    # Pick a random subset of tenants to have maintenance issues (about 40% of them)
    num_issues = max(1, int(len(tenants) * 0.4))
    tenants_with_issues = random.sample(tenants, k=num_issues)
    
    for tenant in tenants_with_issues:
        if not tenant.unit:
            continue
            
        # Using exact choices from STATUS_CHOICES
        status = random.choice(['pending', 'in_progress', 'completed'])
        days_ago = random.randint(1, 45)
        fake_date = now - timedelta(days=days_ago)
        
        req = MaintenanceRequest.objects.create(
            tenant=tenant,
            unit=tenant.unit,
            description=random.choice(maintenance_issues),
            status=status
        )
        
        backdate_model(MaintenanceRequest, req.id, 'created_at', fake_date)

    print("\nSuccess! Dummy bills, inquiries, and maintenance requests generated.")

if __name__ == '__main__':
    generate_dummy_data()