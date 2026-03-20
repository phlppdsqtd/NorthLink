from django.db import models

class Building(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Unit(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='units')
    unit_code = models.CharField(max_length=20, unique=True) # e.g., NG202
    unit_type = models.CharField(max_length=50, blank=True)
    capacity = models.IntegerField(default=1)
    occupancy = models.IntegerField(default=0)
    room_size = models.CharField(max_length=50, blank=True, null=True)
    furnish = models.CharField(max_length=100, blank=True, null=True)
    restroom = models.CharField(max_length=50, blank=True, null=True)
    curfew = models.CharField(max_length=50, blank=True, null=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='Available') # Available, Occupied, Maintenance

    def __str__(self):
        return f"{self.building.name} - {self.unit_code}"
    
class Inquiry(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='inquiries')
    prospect_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False) # Lets staff mark it as "Contacted"

    def __str__(self):
        return f"Inquiry from {self.prospect_name} for {self.unit.unit_code}"