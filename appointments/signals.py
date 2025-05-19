from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment, Notification

@receiver(post_save, sender=Appointment)
def create_notification_on_appointment_status_change(sender, instance, created, **kwargs):
    """
    Crée des notifications lorsqu'un rendez-vous est créé ou que son statut est modifié.
    """
    # Si un rendez-vous vient d'être créé
    if created:
        # Notifier le client
        Notification.objects.create(
            recipient=instance.client,
            appointment=instance,
            notification_type='appointment_created',
            message=f"Votre rendez-vous pour le {instance.appointment_date.strftime('%d/%m/%Y à %H:%M')} a été créé avec succès."
        )
        
        # Notifier les administrateurs (tous les utilisateurs avec is_admin=True)
        for admin in instance.client.__class__.objects.filter(is_admin=True):
            Notification.objects.create(
                recipient=admin,
                appointment=instance,
                notification_type='appointment_created',
                message=f"Nouveau rendez-vous créé par {instance.client.get_full_name()} pour le {instance.appointment_date.strftime('%d/%m/%Y à %H:%M')}."
            )
    
    # Si le statut a été mis à jour
    else:
        # Récupérer les modifications - cette approche simplifiée suppose que le statut a peut-être changé
        previous_instance = Appointment.objects.filter(pk=instance.pk).first()
        if previous_instance and previous_instance.status != instance.status:
            # Notification pour le client
            status_message = {
                'confirmé': f"Votre rendez-vous pour le {instance.appointment_date.strftime('%d/%m/%Y à %H:%M')} a été confirmé et assigné à un laveur.",
                'en cours': f"Le lavage de votre véhicule a commencé.",
                'terminé': f"Le lavage de votre véhicule est terminé. Merci pour votre confiance !",
                'annulé': f"Votre rendez-vous pour le {instance.appointment_date.strftime('%d/%m/%Y à %H:%M')} a été annulé."
            }
            
            if instance.status in status_message:
                # Notifier le client
                Notification.objects.create(
                    recipient=instance.client,
                    appointment=instance,
                    notification_type=f"appointment_{instance.status}",
                    message=status_message[instance.status]
                )
                
                # Notifier l'employé s'il est assigné
                if instance.employee and instance.status in ['confirmed', 'in_progress', 'completed']:
                    employee_message = {
                        'confirmed': f"Un nouveau lavage vous a été assigné pour le {instance.appointment_date.strftime('%d/%m/%Y à %H:%M')}.",
                        'in_progress': f"Vous avez commencé le lavage du véhicule de {instance.client.get_full_name()}.",
                        'completed': f"Vous avez terminé le lavage du véhicule de {instance.client.get_full_name()}. Bon travail !"
                    }
                    
                    Notification.objects.create(
                        recipient=instance.employee,
                        appointment=instance,
                        notification_type=f"appointment_{instance.status}",
                        message=employee_message[instance.status]
                    )

# Vous pouvez également créer un signal pour envoyer des rappels de rendez-vous
# Ce signal serait normalement déclenché par une tâche périodique (via Celery ou Django Q)
def send_appointment_reminder(appointment):
    """
    Envoie un rappel de rendez-vous au client et à l'employé assigné
    """
    # Rappel pour le client
    Notification.objects.create(
        recipient=appointment.client,
        appointment=appointment,
        notification_type='appointment_reminder',
        message=f"Rappel: Vous avez un rendez-vous demain à {appointment.appointment_date.strftime('%H:%M')} pour le lavage de votre véhicule."
    )
    
    # Rappel pour l'employé s'il est assigné
    if appointment.employee:
        Notification.objects.create(
            recipient=appointment.employee,
            appointment=appointment,
            notification_type='appointment_reminder',
            message=f"Rappel: Vous avez un lavage prévu demain à {appointment.appointment_date.strftime('%H:%M')} pour {appointment.client.get_full_name()}."
        )