from django.shortcuts import render
from services.models import Service, ServiceCategory

def home(request):
    categories = ServiceCategory.objects.all()
    featured_services = Service.objects.filter(is_active=True)[:3]
    return render(request, 'home.html', {
        'categories': categories,
        'featured_services': featured_services
    }) 