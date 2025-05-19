from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from .forms import UserRegistrationForm, UserUpdateForm, EmployeeForm
from .models import User, Vehicle
from appointments.models import Appointment
from services.models import Service

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Votre compte a été créé avec succès !')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            
            # Si l'utilisateur est un administrateur et essaie d'accéder au tableau de bord admin
            if user.is_admin and 'admin/dashboard' in next_url:
                return redirect('admin_dashboard')
            
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'accounts/login.html')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour !')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    vehicles = Vehicle.objects.filter(owner=request.user)
    return render(request, 'accounts/profile.html', {
        'form': form,
        'vehicles': vehicles
    })

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        year = request.POST.get('year')
        license_plate = request.POST.get('license_plate')
        color = request.POST.get('color')
        
        vehicle = Vehicle.objects.create(
            owner=request.user,
            brand=brand,
            model=model,
            year=year,
            license_plate=license_plate,
            color=color
        )
        messages.success(request, 'Véhicule ajouté avec succès !')
        return redirect('profile')
    
    return render(request, 'accounts/add_vehicle.html')

@login_required
@user_passes_test(lambda u: u.is_admin)
def employee_list(request):
    employees = User.objects.filter(is_employee=True)
    return render(request, 'accounts/employee_list.html', {
        'employees': employees
    })

@login_required
@user_passes_test(lambda u: u.is_admin)
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'L\'employé a été ajouté avec succès !')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    
    return render(request, 'accounts/add_employee.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_admin)
def edit_employee(request, employee_id):
    employee = get_object_or_404(User, id=employee_id, is_employee=True)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Employé modifié avec succès !')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'accounts/employee_form.html', {
        'form': form,
        'title': 'Modifier un employé'
    })

@login_required
@user_passes_test(lambda u: u.is_admin)
def delete_employee(request, employee_id):
    employee = get_object_or_404(User, id=employee_id, is_employee=True)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employé supprimé avec succès !')
        return redirect('employee_list')
    return render(request, 'accounts/employee_confirm_delete.html', {
        'employee': employee
    })

@login_required
def edit_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    
    if request.method == 'POST':
        vehicle.brand = request.POST.get('brand')
        vehicle.model = request.POST.get('model')
        vehicle.year = request.POST.get('year')
        vehicle.license_plate = request.POST.get('license_plate')
        vehicle.color = request.POST.get('color')
        vehicle.save()
        
        messages.success(request, 'Véhicule modifié avec succès !')
        return redirect('profile')
    
    return render(request, 'accounts/edit_vehicle.html', {
        'vehicle': vehicle
    })

@login_required
def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Véhicule supprimé avec succès !')
        return redirect('profile')
    
    return render(request, 'accounts/delete_vehicle.html', {
        'vehicle': vehicle
    })

@login_required
@user_passes_test(lambda u: u.is_admin)
def admin_dashboard(request):
    # Statistiques générales
    today = timezone.now()
    first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Revenus du mois
    monthly_revenue = Appointment.objects.filter(
        date__gte=first_day_of_month,
        status='completed'
    ).aggregate(total=Sum('service__price'))['total'] or 0
    
    # Services réalisés
    completed_services = Appointment.objects.filter(
        status='completed'
    ).count()
    
    # Taux de fidélité (clients ayant plus d'un rendez-vous)
    total_clients = User.objects.filter(is_employee=False).count()
    loyal_clients = User.objects.filter(
        is_employee=False,
        appointments__count__gt=1
    ).distinct().count()
    loyalty_rate = (loyal_clients / total_clients * 100) if total_clients > 0 else 0
    
    # Rendez-vous en attente
    pending_appointments = Appointment.objects.filter(status='pending').count()
    
    # Liste des employés
    employees = User.objects.filter(is_employee=True).select_related('profile')
    
    # Liste des rendez-vous avec les relations nécessaires
    appointments = Appointment.objects.select_related(
        'user', 'service', 'vehicle'
    ).prefetch_related(
        'employees'
    ).all().order_by('-date')
    
    # Services les plus demandés
    top_services = Service.objects.annotate(
        count=Count('appointments'),
        revenue=Sum('appointments__service__price')
    ).order_by('-count')[:5]
    
    # Rapports périodiques
    reports = [
        {
            'period': 'Aujourd\'hui',
            'revenue': Appointment.objects.filter(
                date__date=today.date(),
                status='completed'
            ).aggregate(total=Sum('service__price'))['total'] or 0,
            'services': Appointment.objects.filter(
                date__date=today.date(),
                status='completed'
            ).count(),
            'customers': Appointment.objects.filter(
                date__date=today.date()
            ).values('user').distinct().count()
        },
        {
            'period': 'Cette semaine',
            'revenue': Appointment.objects.filter(
                date__gte=today - timedelta(days=7),
                status='completed'
            ).aggregate(total=Sum('service__price'))['total'] or 0,
            'services': Appointment.objects.filter(
                date__gte=today - timedelta(days=7),
                status='completed'
            ).count(),
            'customers': Appointment.objects.filter(
                date__gte=today - timedelta(days=7)
            ).values('user').distinct().count()
        },
        {
            'period': 'Ce mois',
            'revenue': monthly_revenue,
            'services': Appointment.objects.filter(
                date__gte=first_day_of_month,
                status='completed'
            ).count(),
            'customers': Appointment.objects.filter(
                date__gte=first_day_of_month
            ).values('user').distinct().count()
        }
    ]
    
    context = {
        'monthly_revenue': monthly_revenue,
        'completed_services': completed_services,
        'loyalty_rate': round(loyalty_rate, 1),
        'pending_appointments': pending_appointments,
        'employees': employees,
        'appointments': appointments,
        'top_services': top_services,
        'reports': reports
    }
    
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_admin)
def assign_employees(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        employee_ids = request.POST.getlist('employees')
        appointment.employees.set(employee_ids)
        appointment.status = 'accepted'
        appointment.save()
        messages.success(request, 'Les employés ont été assignés avec succès !')
        return redirect('admin_dashboard')
    
    employees = User.objects.filter(is_employee=True, is_active=True)
    return render(request, 'accounts/assign_employees.html', {
        'appointment': appointment,
        'employees': employees
    })

@login_required
@user_passes_test(lambda u: u.is_admin)
def daily_report(request):
    today = timezone.now().date()
    appointments = Appointment.objects.filter(date__date=today)
    
    context = {
        'date': today,
        'appointments': appointments,
        'total_revenue': appointments.filter(status='completed').aggregate(total=Sum('service__price'))['total'] or 0,
        'completed_services': appointments.filter(status='completed').count(),
        'pending_services': appointments.filter(status='pending').count(),
        'cancelled_services': appointments.filter(status='cancelled').count()
    }
    
    return render(request, 'accounts/reports/daily_report.html', context)

@login_required
@user_passes_test(lambda u: u.is_admin)
def weekly_report(request):
    today = timezone.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    appointments = Appointment.objects.filter(
        date__date__gte=start_of_week.date(),
        date__date__lte=end_of_week.date()
    )
    
    context = {
        'start_date': start_of_week.date(),
        'end_date': end_of_week.date(),
        'appointments': appointments,
        'total_revenue': appointments.filter(status='completed').aggregate(total=Sum('service__price'))['total'] or 0,
        'completed_services': appointments.filter(status='completed').count(),
        'pending_services': appointments.filter(status='pending').count(),
        'cancelled_services': appointments.filter(status='cancelled').count()
    }
    
    return render(request, 'accounts/reports/weekly_report.html', context)

@login_required
@user_passes_test(lambda u: u.is_admin)
def monthly_report(request):
    today = timezone.now()
    start_of_month = today.replace(day=1)
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    appointments = Appointment.objects.filter(
        date__date__gte=start_of_month.date(),
        date__date__lte=end_of_month.date()
    )
    
    context = {
        'start_date': start_of_month.date(),
        'end_date': end_of_month.date(),
        'appointments': appointments,
        'total_revenue': appointments.filter(status='completed').aggregate(total=Sum('service__price'))['total'] or 0,
        'completed_services': appointments.filter(status='completed').count(),
        'pending_services': appointments.filter(status='pending').count(),
        'cancelled_services': appointments.filter(status='cancelled').count()
    }
    
    return render(request, 'accounts/reports/monthly_report.html', context)

def home(request):
    # Sample featured services
    featured_services = [
        {
            'id': 1,
            'name': 'Lavage Premium',
            'description': 'Un nettoyage complet intérieur et extérieur avec protection céramique.',
            'price': '89.99',
            'duration': '120',
            'image': 'https://images.unsplash.com/photo-1552930294-6b595f4c2974'
        },
        {
            'id': 2,
            'name': 'Polissage & Protection',
            'description': 'Restaurez l\'éclat de votre véhicule avec notre service de polissage professionnel.',
            'price': '129.99',
            'duration': '180',
            'image': 'https://images.unsplash.com/photo-1601362840469-51e4d8d58785'
        },
        {
            'id': 3,
            'name': 'Nettoyage Express',
            'description': 'Un lavage rapide mais efficace pour les clients pressés.',
            'price': '29.99',
            'duration': '45',
            'image': 'https://images.unsplash.com/photo-1520340356584-f9917d1eea6f'
        }
    ]
    
    return render(request, 'home.html', {'featured_services': featured_services})
