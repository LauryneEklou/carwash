from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Transforme un utilisateur en administrateur'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nom d\'utilisateur à transformer en administrateur')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            user.is_admin = True
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'L\'utilisateur {username} est maintenant administrateur'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'L\'utilisateur {username} n\'existe pas')) 