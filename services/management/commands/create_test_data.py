from django.core.management.base import BaseCommand
from services.models import Service, ServiceCategory

class Command(BaseCommand):
    help = 'Crée des données de test pour les services et catégories'

    def handle(self, *args, **kwargs):
        # Création des catégories
        categories = {
            'Lavage': 'Services de lavage extérieur et intérieur',
            'Polish': 'Services de polish et de finition',
            'Détailage': 'Services de détailage complet',
        }
        
        for name, description in categories.items():
            ServiceCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
        
        # Création des services
        services = [
            {
                'name': 'Lavage extérieur',
                'description': 'Lavage complet de l\'extérieur du véhicule',
                'price': 15.00,
                'duration': 30,
                'categories': ['Lavage']
            },
            {
                'name': 'Lavage intérieur',
                'description': 'Nettoyage complet de l\'intérieur du véhicule',
                'price': 25.00,
                'duration': 45,
                'categories': ['Lavage']
            },
            {
                'name': 'Polish complet',
                'description': 'Polish professionnel avec cire',
                'price': 50.00,
                'duration': 120,
                'categories': ['Polish']
            },
            {
                'name': 'Détailage complet',
                'description': 'Service complet incluant lavage, polish et nettoyage intérieur',
                'price': 80.00,
                'duration': 180,
                'categories': ['Détailage', 'Lavage', 'Polish']
            },
        ]
        
        for service_data in services:
            categories = service_data.pop('categories')
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                for category_name in categories:
                    category = ServiceCategory.objects.get(name=category_name)
                    service.categories.add(category)
        
        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès !')) 