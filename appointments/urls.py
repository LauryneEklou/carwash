from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointment_list, name='appointments'),
    path('create/', views.create_appointment, name='create_appointment'),
    path('<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('<int:appointment_id>/receipt/', views.generate_receipt, name='generate_receipt'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('<int:appointment_id>/assign/', views.assign_employee_to_appointment, name='assign_employee_to_appointment'),
    
    path('washer/appointments/', views.washer_appointments, name='washer_appointments'),
    path('<int:appointment_id>/update-status/', views.update_appointment_status, name='update_appointment_status'),
    
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]