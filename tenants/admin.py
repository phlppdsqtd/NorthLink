from django.contrib import admin
from .models import TenantProfile, Inquiry




@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):


    list_display = (
        'get_username',
        'get_first_name',
        'get_last_name',
        'unit',
        'contact_number',
        'term_lease',
        'lease_start',
        'lease_end'
    )


    list_filter = (
        'unit__building',
        'lease_start',
        'lease_end'
    )


    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'unit__unit_code'
    )


    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Unit Assignment', {
            'fields': ('unit',)
        }),
        ('Tenant Details', {
            'fields': (
                'contact_number',
                'term_lease',
                'lease_start',
                'lease_end'
            )
        }),
    )


    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'


    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'
    get_first_name.admin_order_field = 'user__first_name'


    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'
    get_last_name.admin_order_field = 'user__last_name'



@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'message', 'created_at')
    search_fields = ('tenant__user__username', 'message')
    list_filter = ('created_at',)

