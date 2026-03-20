from django.db import models
from django.contrib.auth.models import User
from properties.models import Unit

class TenantProfile(models.Model):
    # Links to the built-in Django User (handles username, password, first_name, last_name)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    
    # Links to the physical room
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenants')
    
    # Extra tenant details from your CSV
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    lease_start = models.DateField(blank=True, null=True)
    lease_end = models.DateField(blank=True, null=True)
    term_lease = models.IntegerField(default=0, help_text="Duration in months")

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.unit.unit_code if self.unit else 'No Unit'})"