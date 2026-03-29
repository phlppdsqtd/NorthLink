from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from properties.models import Unit, Building
from billing.models import Bill
from maintenance.models import MaintenanceRequest
from tenants.models import TenantProfile, Inquiry


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
    total_inquiries = Inquiry.objects.count()
    recent_inquiries = Inquiry.objects.order_by('-created_at')[:5]
    
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
        'total_inquiries': total_inquiries,
        'recent_inquiries': recent_inquiries,
        
        # Breakdowns
        'buildings_data': buildings_data,
        'unit_types': unit_types,
        'billing_breakdown': billing_breakdown,
        
        # Chart data
        'maintenance_chart_data': maintenance_chart_data,
        'building_labels': building_labels,
        'building_occupancy': building_occupancy,
    }
    
    return render(request, "admin_dashboard/dashboard.html", context)