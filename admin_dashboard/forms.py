from django import forms
from properties.models import Unit, Building
from tenants.models import TenantProfile
from billing.models import Bill
from django.contrib.auth.models import User

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['building', 'unit_code', 'unit_type', 'capacity', 'occupancy', 'room_size', 'furnish', 'restroom', 'curfew', 'monthly_rent', 'status']
        widgets = {
            'building': forms.Select(attrs={'class': 'form-control'}),
            'unit_code': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_type': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'occupancy': forms.NumberInput(attrs={'class': 'form-control'}),
            'room_size': forms.TextInput(attrs={'class': 'form-control'}),
            'furnish': forms.TextInput(attrs={'class': 'form-control'}),
            'restroom': forms.TextInput(attrs={'class': 'form-control'}),
            'curfew': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_rent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class TenantForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = TenantProfile
        fields = ['unit', 'contact_number', 'lease_start', 'lease_end', 'term_lease']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'lease_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lease_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'term_lease': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['tenant', 'bill_type', 'amount', 'due_date', 'status']
        widgets = {
            'tenant': forms.Select(attrs={'class': 'form-control'}),
            'bill_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }