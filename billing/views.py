from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from billing.models import Bill


@login_required
def view_bills(request):
    user = request.user


    # Safe tenant fetch
    tenant = getattr(user, 'tenant_profile', None)


    if tenant:
        print("TENANT ID:", tenant.id)


        bills = Bill.objects.filter(tenant_id=tenant.id).order_by('-created_at')
    else:
        print("NO TENANT PROFILE FOUND")
        bills = []


    print("BILLS FOUND IN VIEW:", len(bills))


    return render(request, 'tenants/bills.html', {
        'tenant': tenant,
        'bills': bills
    })

