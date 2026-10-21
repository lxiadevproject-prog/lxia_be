import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import UserProfile, Role


class Command(BaseCommand):
    help = 'Crea de forma segura e idenpotente un superusuario inicial a partir de variables de entorno.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nombre de usuario para el superadmin')
        parser.add_argument('--email', type=str, help='Correo electronico para el superadmin')
        parser.add_argument('--password', type=str, help='Contrasena para el superadmin')

    def handle(self, *args, **options):
        username = options.get('username') or os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = options.get('email') or os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = options.get('password') or os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "[setup_admin] DJANGO_SUPERUSER_USERNAME o DJANGO_SUPERUSER_PASSWORD no estan definidos. Omitiendo creacion automatica."
                )
            )
            return

        user = User.objects.filter(username=username).first()

        if user:
            self.stdout.write(
                self.style.SUCCESS(f"[setup_admin] El superusuario '{username}' ya existe. Verificando perfil...")
            )
            profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': Role.SUPERADMIN})
            if profile.role != Role.SUPERADMIN:
                profile.role = Role.SUPERADMIN
                profile.save(update_fields=['role'])
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': Role.SUPERADMIN})
        if profile.role != Role.SUPERADMIN:
            profile.role = Role.SUPERADMIN
            profile.save(update_fields=['role'])

        self.stdout.write(
            self.style.SUCCESS(f"[setup_admin] Superusuario '{username}' ({email}) creado exitosamente con rol SUPERADMIN.")
        )
