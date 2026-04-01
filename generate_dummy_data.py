import os
import django
import random
from datetime import timedelta

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
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
    print("--- Starting Bulk Dummy Data Generation (Last 60 Days + Current Month) ---")
    
    tenants = list(TenantProfile.objects.select_related('unit').all())
    units = list(Unit.objects.all())
    
    if not tenants or not units:
        print("Error: No tenants or units found! Please run your import_units.py first.")
        return

    now = timezone.now()
    
    # We will spread data across the last 60 days (covers this month and last month)
    TIME_WINDOW_DAYS = 60
    
    # ==========================================
    # 1. GENERATE INQUIRIES
    # ==========================================
    print("Generating Inquiries...")
    
    # Expanded lists for dynamic generation
    first_names = ["Mark", "Sarah", "John", "Maria", "Peter", "Ana", "Miguel", "Luis", "Carmen", "Jose", "Teresa", "Paolo", "Elena", "Ramon", "Rosa", "Grace", "David", "Sofia", "Juan", "Diana"]
    last_names = ["Santos", "Lee", "Doe", "Garcia", "Lim", "Reyes", "Cruz", "Bautista", "Torres", "Aquino", "Mendoza", "Gomez", "Rojas", "Dela Cruz", "Navarro", "Flores", "Villanueva", "Perez", "Castillo", "Rivera"]
    
    messages = [
        "Looking for a single room next month.",
        "Do you have units with a private restroom?",
        "Is there a curfew for the building?",
        "Interested in a bedspace starting next week.",
        "Can I schedule a viewing this Saturday?",
        "What are the requirements for moving in?",
        "Do you allow pets in the building?",
        "Is parking available for a motorcycle?",
        "How much is the initial deposit?",
        "Are visitors allowed overnight?",
        "Does the unit come with air conditioning?",
        "Is water and electricity included in the rent?",
        "Can I pay the rent via bank transfer?",
        "Are there laundry facilities nearby?",
        "I need a place for 6 months, is that possible?",
        "Do you have a family-sized unit available?",
        "Is the internet connection stable for WFH?",
        "When is the earliest I can move in?",
        "Can I cook inside the unit?",
        "Is there a gym or recreational area?"
    ]
    
    TARGET_INQUIRIES = 25
    generated_signatures = set()
    inquiries_created = 0
    attempts = 0 # Safety counter
    
    # Generate unique inquiries until we hit our target
    while inquiries_created < TARGET_INQUIRIES and attempts < 1000:
        attempts += 1
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        msg = random.choice(messages)
        
        # Unique signature to prevent duplicate exact inquiries
        signature = (name, msg)
        
        if signature not in generated_signatures:
            generated_signatures.add(signature)
            
            random_unit = random.choice(units)
            # Generate random PH mobile number
            phone = f"09{random.randint(10, 99)}{random.randint(1000000, 9999999)}"
            
            days_ago = random.randint(0, TIME_WINDOW_DAYS)
            fake_date = now - timedelta(days=days_ago)
            
            # Older inquiries are more likely to be resolved
            is_resolved = True if days_ago > 15 else random.choice([True, False])
            
            inquiry = Inquiry.objects.create(
                unit=random_unit,
                prospect_name=name,
                contact_number=phone,
                message=msg,
                is_resolved=is_resolved
            )
            backdate_model(Inquiry, inquiry.id, 'created_at', fake_date)
            inquiries_created += 1

    # ==========================================
    # 2. GENERATE BILLS
    # ==========================================
    print("Generating Bills...")
    bill_types = ['rent', 'electricity', 'water'] 
    
    for tenant in tenants:
        if not tenant.unit:
            continue
            
        # A. Generate historical bills (Last 60 days)
        num_bills = random.randint(4, 8)
        for _ in range(num_bills):
            b_type = random.choice(bill_types)
            
            if b_type == 'rent':
                amount = tenant.unit.monthly_rent
            elif b_type == 'electricity':
                amount = random.uniform(800, 2500)
            else: 
                amount = random.uniform(150, 600)

            # Random due date within the 60-day window
            days_ago_due = random.randint(0, TIME_WINDOW_DAYS)
            due_date = (now - timedelta(days=days_ago_due)).date()
            
            # If the bill is older than 14 days, it's highly likely to be paid. 
            if days_ago_due > 14:
                status = random.choices(['paid', 'unpaid'], weights=[0.9, 0.1])[0]
            else:
                status = random.choices(['paid', 'unpaid'], weights=[0.4, 0.6])[0]
            
            bill = Bill.objects.create(
                tenant=tenant,
                bill_type=b_type,
                amount=round(amount, 2),
                status=status,
                due_date=due_date
            )
            
            created_date = now - timedelta(days=days_ago_due + 5) 
            backdate_model(Bill, bill.id, 'created_at', created_date)

        # B. GUARANTEED CURRENT MONTH REVENUE
        # Give 80% of tenants a guaranteed paid rent bill for today
        if random.random() < 0.8:
            Bill.objects.create(
                tenant=tenant,
                bill_type='rent',
                amount=tenant.unit.monthly_rent,
                status='paid',
                due_date=now.date()
                # Notice we do NOT backdate this one, so it registers exactly on the current day/month!
            )

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
        "Toilet won't flush",
        "Internet cable port is loose",
        "Peeling paint on the ceiling"
    ]
    
    # Give about 70% of tenants a maintenance issue for a meatier dataset
    num_issues = max(1, int(len(tenants) * 0.7))
    tenants_with_issues = random.sample(tenants, k=num_issues)
    
    for tenant in tenants_with_issues:
        if not tenant.unit:
            continue
            
        # Create 1 or 2 issues per selected tenant
        for _ in range(random.randint(1, 2)):
            days_ago = random.randint(0, TIME_WINDOW_DAYS)
            fake_date = now - timedelta(days=days_ago)
            
            # Logic to make older tickets "completed" and newer ones "pending/in_progress"
            if days_ago > 20:
                status = 'completed'
            elif days_ago > 5:
                status = random.choice(['in_progress', 'completed'])
            else:
                status = random.choice(['pending', 'in_progress'])
            
            req = MaintenanceRequest.objects.create(
                tenant=tenant,
                unit=tenant.unit,
                description=random.choice(maintenance_issues),
                status=status
            )
            
            backdate_model(MaintenanceRequest, req.id, 'created_at', fake_date)

    print("\nSuccess! Historical data added, and current month revenue has been populated.")

if __name__ == '__main__':
    generate_dummy_data()