from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from properties.models import Unit, Building
from billing.models import Bill
from maintenance.models import MaintenanceRequest
from tenants.models import TenantProfile
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from .forms import UnitForm, TenantForm, BillForm


def dashboard(request):
    """
    Enhanced Admin Dashboard with comprehensive analytics
    """
    
    # ===== OCCUPANCY METRICS =====
    total_units = Unit.objects.count()
    occupied_units = Unit.objects.filter(occupancy__gt=0).count()
    available_units = Unit.objects.filter(occupancy=0).count()
    maintenance_units = Unit.objects.filter(status='Maintenance').count()
    
    occupancy_rate = round((occupied_units / total_units * 100), 1) if total_units else 0
    
    # ===== TENANT METRICS =====
    total_tenants = TenantProfile.objects.filter(unit__isnull=False).count()
    
    # Leases expiring in next 30 days
    thirty_days_from_now = timezone.now().date() + timedelta(days=30)
    expiring_leases = TenantProfile.objects.filter(
        lease_end__lte=thirty_days_from_now,
        lease_end__gte=timezone.now().date()
    ).count()
    
    # ===== FINANCIAL METRICS =====
    total_revenue = Bill.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    outstanding_bills_count = Bill.objects.filter(status='unpaid').count()
    outstanding_amount = Bill.objects.filter(status='unpaid').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Monthly revenue (current month)
    current_month_start = timezone.now().replace(day=1)
    monthly_revenue = Bill.objects.filter(
        status='paid',
        created_at__gte=current_month_start
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Collection rate
    total_billed = Bill.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    collection_rate = round((total_revenue / total_billed * 100), 1) if total_billed else 0
    
    # ===== MAINTENANCE METRICS =====
    pending_requests = MaintenanceRequest.objects.filter(status='pending').count()
    in_progress_requests = MaintenanceRequest.objects.filter(status='in_progress').count()
    completed_requests = MaintenanceRequest.objects.filter(status='completed').count()
    total_requests = MaintenanceRequest.objects.count()
    
    # Requests this month
    monthly_requests = MaintenanceRequest.objects.filter(
        created_at__gte=current_month_start
    ).count()
    
    # ===== INQUIRY METRICS =====
    # Note: Tenant maintenance requests now use MaintenanceRequest model
    # Prospect inquiries use properties.Inquiry model
    
    # ===== BUILDING BREAKDOWN =====
    buildings_data = []
    for building in Building.objects.all():
        building_units = Unit.objects.filter(building=building)
        total = building_units.count()
        occupied = building_units.filter(occupancy__gt=0).count()
        available = building_units.filter(occupancy=0).count()
        
        buildings_data.append({
            'name': building.name,
            'total_units': total,
            'occupied': occupied,
            'available': available,
            'occupancy_rate': round((occupied / total * 100), 1) if total else 0
        })
    
    # ===== UNIT TYPE BREAKDOWN =====
    unit_types = Unit.objects.values('unit_type').annotate(
        total=Count('id'),
        occupied=Count('id', filter=Q(occupancy__gt=0))
    )
    
    # ===== RECENT MAINTENANCE REQUESTS =====
    recent_maintenance = MaintenanceRequest.objects.select_related(
        'tenant__user', 'unit'
    ).order_by('-created_at')[:5]
    
    # ===== BILLING BY TYPE =====
    billing_breakdown = Bill.objects.values('bill_type').annotate(
        total_amount=Sum('amount'),
        count=Count('id')
    )
    
    # ===== CHART DATA =====
    # Maintenance status for pie chart
    maintenance_chart_data = {
        'labels': ['Pending', 'In Progress', 'Completed'],
        'data': [pending_requests, in_progress_requests, completed_requests],
        'colors': ['#F59E0B', '#3B82F6', '#10B981']
    }
    
    # Occupancy by building for bar chart
    building_labels = [b['name'] for b in buildings_data]
    building_occupancy = [b['occupancy_rate'] for b in buildings_data]
    
    context = {
        # Occupancy
        'total_units': total_units,
        'occupied_units': occupied_units,
        'available_units': available_units,
        'maintenance_units': maintenance_units,
        'occupancy_rate': occupancy_rate,
        
        # Tenants
        'total_tenants': total_tenants,
        'expiring_leases': expiring_leases,
        
        # Financial
        'total_revenue': total_revenue,
        'outstanding_bills_count': outstanding_bills_count,
        'outstanding_amount': outstanding_amount,
        'monthly_revenue': monthly_revenue,
        'collection_rate': collection_rate,
        
        # Maintenance
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'completed_requests': completed_requests,
        'total_requests': total_requests,
        'monthly_requests': monthly_requests,
        'recent_maintenance': recent_maintenance,
        
        # Inquiries
        # 'total_inquiries': total_inquiries,
        # 'recent_inquiries': recent_inquiries,
        
        # Breakdowns
        'buildings_data': buildings_data,
        'unit_types': unit_types,
        'billing_breakdown': billing_breakdown,
        
        # Chart data
        'maintenance_chart_data': maintenance_chart_data,
        'building_labels': building_labels,
        'building_occupancy': building_occupancy,

        # Page context
        'page_title': 'Admin Dashboard',
        'page_subtitle': 'Real-time analytics and property management overview',
        'show_create_button': False
    }
    
    return render(request, "admin_dashboard/dashboard.html", context)


# ===== CUSTOM ADMIN VIEWS =====

# Units Management
def unit_list(request):
    units = Unit.objects.select_related('building').all()
    return render(request, 'admin_dashboard/unit_list.html', {
        'units': units,
        'page_title': 'Unit Management',
        'page_subtitle': 'Manage all units in your properties',
        'show_create_button': True,
        'create_url': 'admin_dashboard:unit_create',
        'create_button_text': 'Create Unit'
    })

def unit_create(request):
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unit created successfully!')
            return redirect('admin_dashboard:unit_list')
    else:
        form = UnitForm()
    return render(request, 'admin_dashboard/unit_form.html', {
        'form': form, 
        'title': 'Create Unit',
        'page_title': 'Create Unit',
        'page_subtitle': 'Add a new unit to your property',
        'show_create_button': False
    })

def unit_edit(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unit updated successfully!')
            return redirect('admin_dashboard:unit_list')
    else:
        form = UnitForm(instance=unit)
    return render(request, 'admin_dashboard/unit_form.html', {
        'form': form, 
        'title': 'Edit Unit',
        'page_title': 'Edit Unit',
        'page_subtitle': f'Update details for {unit.unit_code}',
        'show_create_button': False
    })

def unit_delete(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    if request.method == 'POST':
        unit.delete()
        messages.success(request, 'Unit deleted successfully!')
        return redirect('admin_dashboard:unit_list')
    return render(request, 'admin_dashboard/unit_confirm_delete.html', {'unit': unit})

# Tenants Management
def tenant_list(request):
    tenants = TenantProfile.objects.select_related('user', 'unit').all()
    return render(request, 'admin_dashboard/tenant_list.html', {
        'tenants': tenants,
        'page_title': 'Tenant Management',
        'page_subtitle': 'Manage all tenants in your properties',
        'show_create_button': True,
        'create_url': 'admin_dashboard:tenant_create',
        'create_button_text': 'Create Tenant'
    })

def tenant_create(request):
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create user first
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data.get('password') or 'defaultpassword123'
                )
                # Create tenant profile
                tenant = form.save(commit=False)
                tenant.user = user
                tenant.save()
            messages.success(request, 'Tenant created successfully!')
            return redirect('admin_dashboard:tenant_list')
    else:
        form = TenantForm()
    return render(request, 'admin_dashboard/tenant_form.html', {'form': form, 'title': 'Create Tenant'})

def tenant_edit(request, pk):
    tenant = get_object_or_404(TenantProfile, pk=pk)
    if request.method == 'POST':
        form = TenantForm(request.POST, instance=tenant)
        if form.is_valid():
            form.save()
            # Update user fields
            user = tenant.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Tenant updated successfully!')
            return redirect('admin_dashboard:tenant_list')
    else:
        initial_data = {
            'username': tenant.user.username,
            'first_name': tenant.user.first_name,
            'last_name': tenant.user.last_name,
            'email': tenant.user.email,
        }
        form = TenantForm(instance=tenant, initial=initial_data)
    return render(request, 'admin_dashboard/tenant_form.html', {'form': form, 'title': 'Edit Tenant'})

def tenant_delete(request, pk):
    tenant = get_object_or_404(TenantProfile, pk=pk)
    if request.method == 'POST':
        user = tenant.user
        tenant.delete()
        user.delete()
        messages.success(request, 'Tenant deleted successfully!')
        return redirect('admin_dashboard:tenant_list')
    return render(request, 'admin_dashboard/tenant_confirm_delete.html', {'tenant': tenant})

# Bills Management
def bill_list(request):
    bills = Bill.objects.select_related('tenant__user').all()
    return render(request, 'admin_dashboard/bill_list.html', {
        'bills': bills,
        'page_title': 'Bill Management',
        'page_subtitle': 'Manage all bills and payments',
        'show_create_button': True,
        'create_url': 'admin_dashboard:bill_create',
        'create_button_text': 'Create Bill'
    })

def bill_create(request):
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bill created successfully!')
            return redirect('admin_dashboard:bill_list')
    else:
        form = BillForm()
    return render(request, 'admin_dashboard/bill_form.html', {'form': form, 'title': 'Create Bill'})

def bill_edit(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bill updated successfully!')
            return redirect('admin_dashboard:bill_list')
    else:
        form = BillForm(instance=bill)
    return render(request, 'admin_dashboard/bill_form.html', {'form': form, 'title': 'Edit Bill'})

def bill_delete(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        bill.delete()
        messages.success(request, 'Bill deleted successfully!')
        return redirect('admin_dashboard:bill_list')
    return render(request, 'admin_dashboard/bill_confirm_delete.html', {'bill': bill})

# Maintenance Management
def maintenance_list(request):
    maintenance_requests = MaintenanceRequest.objects.select_related('tenant__user', 'unit').all()
    return render(request, 'admin_dashboard/maintenance_list.html', {
        'maintenance_requests': maintenance_requests,
        'page_title': 'Maintenance Requests',
        'page_subtitle': 'Manage and update maintenance request statuses',
        'show_create_button': False
    })

def maintenance_update(request, pk):
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['pending', 'in_progress', 'completed']:
            maintenance_request.status = status
            maintenance_request.save()
            messages.success(request, f'Maintenance request status updated to {status.replace("_", " ").title()}!')
        return redirect('admin_dashboard:maintenance_list')
    return render(request, 'admin_dashboard/maintenance_update.html', {'maintenance_request': maintenance_request})