from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list, name='services'),
    path('<int:service_id>/', views.service_detail, name='service_detail'),
] 