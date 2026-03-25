from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Inquiry
from billing.models import Bill


def tenant_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Check if user is a tenant or an admin
            if hasattr(user, 'tenant_profile'):
                return redirect('tenant_dashboard')
            else:
                return redirect('/admin')
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'tenants/login.html')


@login_required
def dashboard(request):
    tenant = getattr(request.user, 'tenant_profile', None)

    # 🔥 FIX: validate tenant properly
    if not tenant or not tenant.unit:
        logout(request)
        return redirect('tenant_login')

    unit = tenant.unit

    # Recent inquiries and bills for the dashboard
    inquiries = Inquiry.objects.filter(tenant=tenant).order_by('-id')[:5]
    bills = Bill.objects.filter(tenant=tenant).order_by('-created_at')[:3]

    return render(request, 'tenants/dashboard.html', {
        'tenant': tenant,
        'unit': unit,
        'inquiries': inquiries,
        'bills': bills,
    })


@login_required
def submit_request(request):
    tenant = getattr(request.user, 'tenant_profile', None)

    # 🔥 FIX: validate tenant
    if not tenant or not tenant.unit:
        logout(request)
        return redirect('tenant_login')

    if request.method == "POST":
        message = request.POST.get("message")
        if message and message.strip():
            Inquiry.objects.create(
                tenant=tenant,
                message=message.strip()
            )
        return redirect('tenant_dashboard')

    return render(request, 'tenants/submit_request.html')


@login_required
def view_bills(request):
    tenant = getattr(request.user, 'tenant_profile', None)

    # 🔥 FIX: validate tenant
    if not tenant or not tenant.unit:
        logout(request)
        return redirect('tenant_login')

    bills = Bill.objects.filter(tenant_id=tenant.id).order_by('-created_at')

    return render(request, 'tenants/bills.html', {
        'tenant': tenant,
        'bills': bills
    })


@login_required
def my_unit(request):
    tenant = getattr(request.user, 'tenant_profile', None)

    # 🔥 FIX: validate tenant
    if not tenant or not tenant.unit:
        logout(request)
        return redirect('tenant_login')

    unit = tenant.unit

    return render(request, 'tenants/my_unit.html', {
        'tenant': tenant,
        'unit': unit
    })