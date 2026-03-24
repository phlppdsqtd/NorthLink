from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from tenants import views as tenant_views  




urlpatterns = [
    path('admin/', admin.site.urls),


    path('tenant/login/', tenant_views.tenant_login, name='tenant_login'),


    path('logout/', auth_views.LogoutView.as_view(next_page='/tenant/login/'), name='logout'),


    path('tenant/', include('tenants.urls')),


    path('', include('properties.urls')),

    path('billing/', include('billing.urls')),
]




if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]

