from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    path('edit-vehicle/<int:vehicle_id>/', views.edit_vehicle, name='edit_vehicle'),
    path('delete-vehicle/<int:vehicle_id>/', views.delete_vehicle, name='delete_vehicle'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/<int:employee_id>/edit/', views.edit_employee, name='edit_employee'),
    path('employees/<int:employee_id>/delete/', views.delete_employee, name='delete_employee'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/assign-employees/<int:appointment_id>/', views.assign_employees, name='assign_employees'),
    path('admin/reports/daily/', views.daily_report, name='daily_report'),
    path('admin/reports/weekly/', views.weekly_report, name='weekly_report'),
    path('admin/reports/monthly/', views.monthly_report, name='monthly_report'),
] 