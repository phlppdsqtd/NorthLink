from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # This represents the root path '' (the homepage)
    path('', views.public_unit_list, name='unit_list'),
]