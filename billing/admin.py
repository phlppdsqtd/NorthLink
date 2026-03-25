from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Bill




@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'bill_type', 'amount', 'status', 'due_date')

