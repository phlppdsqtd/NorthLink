from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Building, Unit, Inquiry

def public_unit_list(request):
    # --- 1. HANDLE INQUIRY SUBMISSION ---
    if request.method == 'POST':
        unit_id = request.POST.get('unit_id')
        name = request.POST.get('name')
        contact = request.POST.get('contact')
        message = request.POST.get('message')

        if unit_id and name and contact:
            unit = Unit.objects.get(id=unit_id)
            Inquiry.objects.create(
                unit=unit, prospect_name=name, contact_number=contact, message=message
            )
            messages.success(request, f"Your inquiry for {unit.unit_code} has been sent! Management will contact you soon.")
        return redirect('properties:unit_list')

    # --- 2. HANDLE THE FILTER BAR ---
    units = Unit.objects.filter(status='Available')
    buildings = Building.objects.all()
    
    # NEW: Get a list of unique unit types (Studio, 1-Bedroom, etc.)
    unit_types = Unit.objects.exclude(unit_type='').values_list('unit_type', flat=True).distinct()

    # Get the dropdown choices from the URL
    building_filter = request.GET.get('building')
    type_filter = request.GET.get('unit_type') # NEW
    sort_by = request.GET.get('sort')

    # Apply the filters
    if building_filter:
        units = units.filter(building__name=building_filter)
        
    if type_filter:
        units = units.filter(unit_type=type_filter) # NEW
    
    if sort_by == 'price_asc':
        units = units.order_by('monthly_rent')
    elif sort_by == 'price_desc':
        units = units.order_by('-monthly_rent')

    context = {
        'units': units,
        'buildings': buildings,
        'unit_types': unit_types, # NEW
        'current_building': building_filter,
        'current_type': type_filter,      # NEW
        'current_sort': sort_by,
    }
    return render(request, 'properties/unit_list.html', context)

def inquiry_list_view(request):
    inquiries = Inquiry.objects.all().order_by('-created_at')
    recent_maintenance = MaintenanceRequest.objects.all().order_by('-created_at')[:5]

    # Calculate Metrics
    total_inquiries = inquiries.count()
    resolved_inquiries = inquiries.filter(is_resolved=True).count()
    unresolved_inquiries = inquiries.filter(is_resolved=False).count()

    # Chart Data (Example: Inquiries per month or status. Adjust to your needs)
    chart_data = {
        'labels': ['Resolved', 'Unresolved'],
        'data': [resolved_inquiries, unresolved_inquiries]
    }

    context = {
        'inquiries': inquiries,
        'recent_maintenance': recent_maintenance,
        'total_inquiries': total_inquiries,
        'resolved_inquiries': resolved_inquiries,
        'unresolved_inquiries': unresolved_inquiries,
        'inquiry_chart_data': json.dumps(chart_data), # Safely pass to JS
    }
    
    return render(request, 'admin_dashboard/inquiry_list.html', context)