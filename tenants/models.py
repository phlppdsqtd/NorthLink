from django.db import models
from django.contrib.auth.models import User
from properties.models import Unit
from django.db.models.signals import post_save
from django.dispatch import receiver




# =========================
# TENANT PROFILE
# =========================
class TenantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')


    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenants')


    contact_number = models.CharField(max_length=20, blank=True, null=True)
    lease_start = models.DateField(blank=True, null=True)
    lease_end = models.DateField(blank=True, null=True)
    term_lease = models.IntegerField(default=0, help_text="Duration in months")


    def __str__(self):
        return f"{self.user.get_full_name()} ({self.unit.unit_code if self.unit else 'No Unit'})"




# =========================
# SIGNALS (FIXED)
# =========================
@receiver(post_save, sender=User)
def create_tenant_profile(sender, instance, created, **kwargs):
    if created and not instance.is_staff and not instance.is_superuser:
        TenantProfile.objects.create(user=instance)




@receiver(post_save, sender=User)
def save_tenant_profile(sender, instance, **kwargs):
    if hasattr(instance, 'tenant_profile'):
        instance.tenant_profile.save()




# =========================
# INQUIRY MODEL
# =========================
class Inquiry(models.Model):
    tenant = models.ForeignKey('TenantProfile', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']  


    def __str__(self):
        return str(self.tenant.user.username) + " - " + str(self.created_at)