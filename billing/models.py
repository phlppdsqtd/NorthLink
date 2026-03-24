from django.db import models

# Create your models here.
from django.db import models
from tenants.models import TenantProfile




class Bill(models.Model):
    BILL_TYPES = [
        ('rent', 'Rent'),
        ('electricity', 'Electricity'),
        ('water', 'Water'),
    ]


    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]


    tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE)
    bill_type = models.CharField(max_length=20, choices=BILL_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.tenant.user.username} - {self.bill_type}"

