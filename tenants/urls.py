from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.tenant_login, name='tenant_login'),
    path('dashboard/', views.dashboard, name='tenant_dashboard'),
    path('submit-request/', views.submit_request, name='submit_request'),
    path('bills/', views.view_bills, name='view_bills'),
    path('my-unit/', views.my_unit, name='my_unit'),
]
