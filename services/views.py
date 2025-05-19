from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Service, ServiceCategory

def service_list(request):
    all_services = Service.objects.filter(is_active=True)
    
    popular_services = Service.objects.filter(is_active=True).annotate(
        appointment_count=Count('appointment')
    ).order_by('-appointment_count')[:3]
    
    categories = ServiceCategory.objects.all()
    
    context = {
        'all_services': all_services,
        'popular_services': popular_services,
        'categories': categories,
    }
    
    return render(request, 'services/service_list.html', context)

def service_detail(request, service_id):
    return render(request, 'services/service_detail.html')

@login_required
def category_services(request, category_id):
    category = get_object_or_404(ServiceCategory, id=category_id)
    services = Service.objects.filter(categories=category, is_active=True)
    return render(request, 'services/category_services.html', {
        'category': category,
        'services': services
    })
