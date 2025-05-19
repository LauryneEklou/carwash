import random
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from accounts.models import Vehicle
from services.models import Service
from appointments.models import Appointment

User = get_user_model()

class Command(BaseCommand):
    help = 'Remplit la base de données avec des données de test'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Nombre de clients à créer')
        parser.add_argument('--employees', type=int, default=3, help='Nombre d\'employés à créer')
        parser.add_argument('--vehicles', type=int, default=10, help='Nombre de véhicules à créer')
        parser.add_argument('--appointments', type=int, default=15, help='Nombre de rendez-vous à créer')

    def handle(self, *args, **options):
        num_users = options['users']
        num_employees = options['employees']
        num_vehicles = options['vehicles']
        num_appointments = options['appointments']

        self.stdout.write(self.style.SUCCESS('Début du seeding de la base de données...'))

        try:
            with transaction.atomic():
                # Création d'un utilisateur administrateur
                admin_user = self._create_admin()
                
                # Création d'employés (laveurs)
                employees = self._create_employees(num_employees)
                
                # Création de clients
                clients = self._create_clients(num_users)
                
                # Création de services
                services = self._create_services()
                
                # Création de véhicules pour les clients
                vehicles = self._create_vehicles(clients, num_vehicles)
                
                # Création de rendez-vous
                appointments = self._create_appointments(clients, employees, vehicles, services, num_appointments)

            self.stdout.write(self.style.SUCCESS('Base de données remplie avec succès !'))
            
            # Afficher les informations de connexion
            self._print_login_info(admin_user, employees, clients)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur pendant le seeding: {str(e)}'))

    def _create_admin(self):
        """Crée un utilisateur administrateur."""
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@carwashpro.fr',
                'first_name': 'Admin',
                'last_name': 'Système',
                'is_staff': True,
                'is_superuser': True,
                'is_admin': True,
                'phone_number': '+33123456789',
                'address': '123 Avenue Principale, Paris'
            }
        )
        
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Utilisateur administrateur créé'))
        else:
            self.stdout.write(self.style.SUCCESS('Utilisateur administrateur existant trouvé'))
            
        return admin

    def _create_employees(self, num_employees):
        """Crée des comptes employés."""
        employees = []
        
        first_names = ['Jean', 'Marie', 'Pierre', 'Sophie', 'Luc', 'Camille', 'Thomas', 'Julie']
        last_names = ['Dupont', 'Martin', 'Dubois', 'Bernard', 'Richard', 'Petit', 'Robert', 'Michel']
        
        for i in range(num_employees):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f'employee{i+1}'
            
            employee, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@carwashpro.fr',
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_employee': True,
                    'phone_number': f'+331234567{i+10}',
                    'address': f'{100+i} Rue des Laveurs, Paris'
                }
            )
            
            if created:
                employee.set_password('employee123')
                employee.save()
                self.stdout.write(self.style.SUCCESS(f'Employé créé : {username}'))
            
            employees.append(employee)
            
        return employees

    def _create_clients(self, num_users):
        """Crée des comptes clients."""
        clients = []
        
        first_names = ['Alexandre', 'Emma', 'Lucas', 'Chloé', 'Maxime', 'Sarah', 'Nathan', 'Léa', 'Hugo', 'Inès']
        last_names = ['Leroy', 'Moreau', 'Fournier', 'Girard', 'Morel', 'Lambert', 'Bonnet', 'Mercier', 'Blanc', 'Rousseau']
        
        for i in range(num_users):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f'client{i+1}'
            
            client, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@exemple.fr',
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone_number': f'+336789012{i+10}',
                    'address': f'{200+i} Boulevard des Clients, Paris'
                }
            )
            
            if created:
                client.set_password('client123')
                client.save()
                self.stdout.write(self.style.SUCCESS(f'Client créé : {username}'))
            
            clients.append(client)
            
        return clients

    def _create_services(self):
        """Crée les services de lavage."""
        services = [
            {
                'name': 'Lavage Extérieur Standard',
                'description': 'Lavage carrosserie, nettoyage vitres et jantes',
                'price': 19.99,
                'duration': 30,
                'is_active': True,
            },
            {
                'name': 'Lavage Intérieur Standard',
                'description': 'Aspiration complète, nettoyage plastiques et vitres',
                'price': 24.99,
                'duration': 45,
                'is_active': True,
            },
            {
                'name': 'Lavage Complet Premium',
                'description': 'Lavage extérieur, intérieur et traitement cire protectrice',
                'price': 39.99,
                'duration': 75,
                'is_active': True,
            },
            {
                'name': 'Détailing Complet',
                'description': 'Lavage complet avec nettoyage approfondi, traitement cuir et plastiques, polish',
                'price': 89.99,
                'duration': 180,
                'is_active': True,
            },
            {
                'name': 'Protection Céramique',
                'description': 'Application de protection céramique pour une brillance et protection durables',
                'price': 129.99,
                'duration': 240,
                'is_active': True,
            },
        ]
        
        created_services = []
        
        for service_data in services:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            created_services.append(service)
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Service créé : {service.name}'))
            
        return created_services

    def _create_vehicles(self, clients, num_vehicles):
        """Crée des véhicules pour les clients."""
        vehicles = []
        
        brands = ['Peugeot', 'Renault', 'Citroën', 'Volkswagen', 'Toyota', 'BMW', 'Mercedes', 'Audi', 'Ford']
        models = {
            'Peugeot': ['208', '308', '3008', '5008'],
            'Renault': ['Clio', 'Megane', 'Captur', 'Kadjar'],
            'Citroën': ['C3', 'C4', 'C5', 'Berlingo'],
            'Volkswagen': ['Golf', 'Polo', 'Tiguan', 'Passat'],
            'Toyota': ['Yaris', 'Corolla', 'RAV4', 'CH-R'],
            'BMW': ['Série 1', 'Série 3', 'Série 5', 'X3'],
            'Mercedes': ['Classe A', 'Classe C', 'Classe E', 'GLC'],
            'Audi': ['A3', 'A4', 'Q3', 'Q5'],
            'Ford': ['Fiesta', 'Focus', 'Puma', 'Kuga']
        }
        colors = ['Noir', 'Blanc', 'Gris', 'Rouge', 'Bleu', 'Vert', 'Argent']
        
        for i in range(num_vehicles):
            client = random.choice(clients)
            brand = random.choice(brands)
            model = random.choice(models[brand])
            year = random.randint(2010, 2025)
            color = random.choice(colors)
            license_plate = f"{''.join(random.choices('ABCDEFGHIJKLMNPQRSTUVWXYZ', k=2))}-{''.join(random.choices('0123456789', k=3))}-{''.join(random.choices('ABCDEFGHIJKLMNPQRSTUVWXYZ', k=2))}"
            
            vehicle, created = Vehicle.objects.get_or_create(
                license_plate=license_plate,
                defaults={
                    'owner': client,
                    'brand': brand,
                    'model': model,
                    'year': year,
                    'color': color
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Véhicule créé : {brand} {model} ({license_plate})'))
            
            vehicles.append(vehicle)
            
        return vehicles

    def _create_appointments(self, clients, employees, vehicles, services, num_appointments):
        """Crée des rendez-vous de lavage."""
        appointments = []
        
        # Statuts possibles avec leur probabilité
        statuses = [
            ('pending', 0.2),  # 20% en attente
            ('confirmed', 0.3),  # 30% confirmés
            ('in_progress', 0.2),  # 20% en cours
            ('completed', 0.2),  # 20% terminés
            ('cancelled', 0.1)  # 10% annulés
        ]
        
        # Dates pour les rendez-vous (de -7 jours à +14 jours)
        start_date = timezone.now() - datetime.timedelta(days=7)
        
        for i in range(num_appointments):
            client = random.choice(clients)
            
            # Sélectionner un véhicule qui appartient à ce client
            client_vehicles = [v for v in vehicles if v.owner == client]
            if not client_vehicles:
                # Si le client n'a pas de véhicule, passer au suivant
                continue
            vehicle = random.choice(client_vehicles)
            
            service = random.choice(services)
            
            # Générer une date dans les 21 prochains jours
            days_offset = random.randint(-7, 14)
            appointment_date = start_date + datetime.timedelta(days=days_offset)
            hour = random.randint(9, 17)
            minute = random.choice([0, 15, 30, 45])
            appointment_date = appointment_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Sélection du statut basé sur les probabilités
            status = random.choices(
                [s[0] for s in statuses],
                weights=[s[1] for s in statuses],
                k=1
            )[0]
            
            # Assigner un employé si le statut n'est pas 'pending'
            employee = None
            if status != 'pending':
                employee = random.choice(employees)
                
            # Créer le rendez-vous
            appointment = Appointment.objects.create(
                client=client,
                employee=employee,
                vehicle=vehicle,
                service=service,
                appointment_date=appointment_date,
                status=status,
                notes=f"Rendez-vous de test #{i+1}"
            )
            
            self.stdout.write(self.style.SUCCESS(
                f'Rendez-vous créé : {client.get_full_name()} - {service.name} - {appointment_date.strftime("%d/%m/%Y %H:%M")} - {status}'
            ))
            
            appointments.append(appointment)
            
        return appointments
        
    def _print_login_info(self, admin, employees, clients):
        """Affiche les informations de connexion pour les utilisateurs créés."""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("INFORMATIONS DE CONNEXION"))
        self.stdout.write("="*50)
        
        self.stdout.write("\nADMINISTRATEUR:")
        self.stdout.write(f"Username: {admin.username}")
        self.stdout.write("Password: admin123")
        
        self.stdout.write("\nEMPLOYÉS (LAVEURS):")
        for i, employee in enumerate(employees):
            self.stdout.write(f"{i+1}. Username: {employee.username}")
            self.stdout.write(f"   Password: employee123")
        
        self.stdout.write("\nCLIENTS:")
        for i, client in enumerate(clients):
            self.stdout.write(f"{i+1}. Username: {client.username}")
            self.stdout.write(f"   Password: client123")
            
        self.stdout.write("\n" + "="*50)
        self.stdout.write("Vous pouvez maintenant vous connecter avec ces identifiants pour tester l'application.")
        self.stdout.write("="*50 + "\n")