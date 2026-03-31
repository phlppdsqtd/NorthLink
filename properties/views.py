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