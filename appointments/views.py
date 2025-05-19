from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Sum
from .models import Appointment, Receipt, Notification
from services.models import Service
from accounts.models import Vehicle, User

@login_required
def appointment_list(request):
    if request.user.is_employee:
        appointments = Appointment.objects.filter(employee=request.user)
    elif request.user.is_admin:
        appointments = Appointment.objects.all()
    else:
        appointments = Appointment.objects.filter(client=request.user)
    
    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments
    })

@login_required
def create_appointment(request):
    if request.method == 'POST':
        service_id = request.POST.get('service')
        vehicle_id = request.POST.get('vehicle')
        appointment_date = request.POST.get('appointment_date')
        notes = request.POST.get('notes', '')
        
        service = get_object_or_404(Service, id=service_id)
        vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
        
        # Vérifier si la date est valide
        try:
            appointment_datetime = datetime.strptime(appointment_date, '%Y-%m-%d %H:%M')
            appointment_datetime = timezone.make_aware(appointment_datetime)
            if appointment_datetime < timezone.now():
                messages.error(request, 'La date de rendez-vous doit être dans le futur.')
                return redirect('create_appointment')
        except ValueError:
            messages.error(request, 'Format de date invalide.')
            return redirect('create_appointment')
        
        appointment = Appointment.objects.create(
            client=request.user,
            service=service,
            vehicle=vehicle,
            appointment_date=appointment_datetime,
            notes=notes
        )
        
        messages.success(request, 'Rendez-vous créé avec succès !')
        return redirect('appointments')
    
    services = Service.objects.filter(is_active=True)
    vehicles = Vehicle.objects.filter(owner=request.user)
    
    # Générer les créneaux disponibles pour les 7 prochains jours
    available_slots = []
    start_date = timezone.now()
    end_date = start_date + timedelta(days=7)
    
    current_date = start_date
    while current_date < end_date:
        if current_date.weekday() < 5:  # Lundi à Vendredi
            for hour in range(9, 18):  # 9h à 17h
                slot = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                available_slots.append(slot)
        current_date += timedelta(days=1)
    
    return render(request, 'appointments/create_appointment.html', {
        'services': services,
        'vehicles': vehicles,
        'available_slots': available_slots
    })

@login_required
def appointment_detail(request, appointment_id):
    if request.user.is_employee:
        appointment = get_object_or_404(Appointment, id=appointment_id, employee=request.user)
    elif request.user.is_admin:
        appointment = get_object_or_404(Appointment, id=appointment_id)
    else:
        appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    
    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment
    })

@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, client=request.user)
    
    if appointment.status == 'pending':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, 'Rendez-vous annulé avec succès.')
    else:
        messages.error(request, 'Ce rendez-vous ne peut pas être annulé.')
    
    return redirect('appointments')

@login_required
def generate_receipt(request, appointment_id):
    if request.user.is_admin:
        appointment = get_object_or_404(Appointment, id=appointment_id)
        if appointment.status == 'completed' and not hasattr(appointment, 'receipt'):
            receipt = Receipt.objects.create(
                appointment=appointment,
                total_amount=appointment.service.price,
                payment_method='Carte bancaire',
                receipt_number=f'RCP-{appointment.id:06d}'
            )
            messages.success(request, 'Reçu généré avec succès.')
        else:
            messages.error(request, 'Impossible de générer le reçu.')
    else:
        messages.error(request, 'Accès non autorisé.')
    
    return redirect('appointment_detail', appointment_id=appointment_id)

@login_required
@user_passes_test(lambda u: u.is_employee)
def employee_dashboard(request):
    today = timezone.now().date()
    appointments = Appointment.objects.filter(
        employee=request.user,
        appointment_date__date=today
    ).order_by('appointment_date')
    
    upcoming_appointments = Appointment.objects.filter(
        employee=request.user,
        appointment_date__date__gt=today
    ).order_by('appointment_date')[:5]
    
    pending_appointments = Appointment.objects.filter(
        employee=request.user,
        status='confirmed'
    ).order_by('appointment_date')
    
    in_progress_appointments = Appointment.objects.filter(
        employee=request.user,
        status='in_progress'
    ).order_by('appointment_date')
    
    completed_appointments = Appointment.objects.filter(
        employee=request.user,
        status='completed',
        appointment_date__date=today
    ).order_by('-appointment_date')[:5]
    
    return render(request, 'appointments/employee_dashboard.html', {
        'today_appointments': appointments,
        'upcoming_appointments': upcoming_appointments,
        'pending_appointments': pending_appointments,
        'in_progress_appointments': in_progress_appointments,
        'completed_appointments': completed_appointments,
        'today_date': today
    })

@login_required
@user_passes_test(lambda u: u.is_admin)
def admin_dashboard(request):
    # Statistiques générales
    total_appointments = Appointment.objects.count()
    total_revenue = Receipt.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_employees = User.objects.filter(is_employee=True).count()
    total_clients = User.objects.filter(is_employee=False, is_admin=False).count()
    
    # Rendez-vous du jour
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        appointment_date__date=today
    ).order_by('appointment_date')
    
    # Services les plus demandés
    popular_services = Service.objects.annotate(
        appointment_count=Count('appointment')
    ).order_by('-appointment_count')[:5]
    
    # Statistiques des rendez-vous par statut
    appointment_stats = Appointment.objects.values('status').annotate(
        count=Count('id')
    )
    
    # Rendez-vous à venir
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__date__gt=today
    ).order_by('appointment_date')[:5]
    
    return render(request, 'appointments/admin_dashboard.html', {
        'total_appointments': total_appointments,
        'total_revenue': total_revenue,
        'total_employees': total_employees,
        'total_clients': total_clients,
        'today_appointments': today_appointments,
        'popular_services': popular_services,
        'appointment_stats': appointment_stats,
        'upcoming_appointments': upcoming_appointments
    })

from accounts.models import User

@login_required
@user_passes_test(lambda u: u.is_admin)
def assign_employee_to_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    employees = User.objects.filter(is_employee=True)

    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        employee = get_object_or_404(User, id=employee_id, is_employee=True)
        appointment.employee = employee
        appointment.status = 'confirmed'
        appointment.save()
        messages.success(request, 'Employé assigné avec succès.')
        return redirect('admin_dashboard')

    return render(request, 'appointments/assign_employees.html', {
        'appointment': appointment,
        'employees': employees
    })

@login_required
@user_passes_test(lambda u: u.is_employee or u.is_admin)
def complete_appointment(request, appointment_id):
    if request.user.is_employee:
        appointment = get_object_or_404(Appointment, id=appointment_id, employee=request.user)
    else:
        appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status == 'confirmed':
        appointment.status = 'completed'
        appointment.completed_at = timezone.now()
        appointment.save()
        messages.success(request, 'Rendez-vous marqué comme terminé.')
    else:
        messages.error(request, 'Ce rendez-vous ne peut pas être marqué comme terminé.')
    
    return redirect('appointment_detail', appointment_id=appointment_id)

@login_required
@user_passes_test(lambda u: u.is_employee)
def washer_appointments(request):
    # Obtenir tous les rendez-vous du laveur, triés par date et statut
    confirmed_appointments = Appointment.objects.filter(
        employee=request.user,
        status='confirmed'
    ).order_by('appointment_date')
    
    in_progress_appointments = Appointment.objects.filter(
        employee=request.user,
        status='in_progress'
    ).order_by('appointment_date')
    
    # Historique des rendez-vous terminés, limité aux 15 derniers jours
    fifteen_days_ago = timezone.now() - timedelta(days=15)
    completed_appointments = Appointment.objects.filter(
        employee=request.user,
        status='completed',
        appointment_date__gte=fifteen_days_ago
    ).order_by('-appointment_date')
    
    return render(request, 'appointments/washer_appointments.html', {
        'confirmed_appointments': confirmed_appointments,
        'in_progress_appointments': in_progress_appointments,
        'completed_appointments': completed_appointments
    })

@login_required
@user_passes_test(lambda u: u.is_employee)
def update_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, employee=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        # Vérifier que le nouveau statut est valide pour un laveur
        if new_status in ['in_progress', 'completed']:
            if new_status == 'in_progress' and appointment.status == 'confirmed':
                appointment.status = 'in_progress'
                appointment.save()
                messages.success(request, 'Le lavage a commencé.')
            elif new_status == 'completed' and appointment.status == 'in_progress':
                appointment.status = 'completed'
                appointment.save()
                messages.success(request, 'Le lavage est terminé.')
            else:
                messages.error(request, 'Transition de statut non autorisée.')
        else:
            messages.error(request, 'Statut non valide.')
            
    # Rediriger vers la page des rendez-vous du laveur
    return redirect('washer_appointments')

@login_required
def notification_list(request):
    """Affiche la liste des notifications de l'utilisateur"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'appointments/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, notification_id):
    """Marque une notification comme lue"""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # Si c'est une requête AJAX, renvoie un statut JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # Sinon, redirige vers la liste des notifications
    return redirect('notification_list')

@login_required
def mark_all_notifications_read(request):
    """Marque toutes les notifications de l'utilisateur comme lues"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'Toutes les notifications ont été marquées comme lues.')
    
    return redirect('notification_list')

# Ajoutez cette fonction pour compter les notifications non lues dans le contexte global
def get_unread_notifications_count(request):
    if request.user.is_authenticated:
        return Notification.objects.filter(recipient=request.user, is_read=False).count()
    return 0