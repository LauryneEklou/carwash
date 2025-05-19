from .models import Notification

def notifications_processor(request):
    """
    Ajoute le nombre de notifications non lues au contexte global.
    Permet d'afficher le compteur de notifications dans la navbar.
    """
    context = {'unread_notifications_count': 0}
    
    if request.user.is_authenticated:
        context['unread_notifications_count'] = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        
    return context