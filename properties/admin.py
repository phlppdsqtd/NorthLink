from django.contrib import admin
from .models import Building, Unit
from .models import Inquiry

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    # Added EVERY column from your physical properties
    list_display = ('unit_code', 'building', 'unit_type', 'capacity', 'occupancy', 'room_size', 'furnish', 'restroom', 'curfew', 'monthly_rent', 'status')
    
    # Made a few of them editable right from the table
    list_editable = ('status', 'monthly_rent', 'occupancy')
    
    list_filter = ('building', 'status', 'unit_type', 'furnish')
    search_fields = ('unit_code',)
    
@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    # What shows up in the table
    list_display = ('prospect_name', 'unit', 'contact_number', 'created_at', 'is_resolved')
    
    # Allows staff to check off inquiries directly from the list view
    list_editable = ('is_resolved',)
    
    # Side filters
    list_filter = ('is_resolved', 'created_at', 'unit__building')
    search_fields = ('prospect_name', 'contact_number', 'unit__unit_code')