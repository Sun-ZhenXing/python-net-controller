from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('v1/networks/', views.networks, name='networks'),
    path('v1/networks/<uuid:uuid>/', views.network_id, name='network_id'),
    path('v1/subnets/', views.subnets, name='subnets'),
    path('v1/subnets/<uuid:uuid>/', views.subnet_id, name='subnet_id'),
    path('v1/ports/', views.ports, name='ports'),
    path('v1/ports/<uuid:uuid>/', views.port_id, name='port_id'),
]
