from django.db import models
from tenants.models import TenantProfile
from properties.models import Unit

class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    tenant = models.ForeignKey(TenantProfile, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.tenant} for {self.unit} - {self.status}"
