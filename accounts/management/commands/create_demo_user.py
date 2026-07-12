from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates a demo user for recruiter/testing access, if one does not already exist.'

    def handle(self, *args, **options):
        email = 'rakib@gmail.com'
        password = 'admin@1234'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Demo user "{email}" already exists. Skipping.'))
            return

        User.objects.create_superuser(email=email, password=password, full_name='Demo User')
        self.stdout.write(self.style.SUCCESS(f'Demo user created: {email} / {password}'))