from django.contrib import admin
from .models import TenantProfile

@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    # Added term_lease, lease_start, and lease_end
    list_display = ('get_username', 'get_first_name', 'get_last_name', 'unit', 'contact_number', 'term_lease', 'lease_start', 'lease_end')
    list_filter = ('unit__building', 'lease_start', 'lease_end')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'unit__unit_code')

    def get_username(self, obj): return obj.user.username
    get_username.short_description = 'Unit Code'

    def get_first_name(self, obj): return obj.user.first_name
    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'user__first_name'

    def get_last_name(self, obj): return obj.user.last_name
    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'user__last_name'