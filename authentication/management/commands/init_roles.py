from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from authentication.signals import ROLE_GROUP_MAPPING


class Command(BaseCommand):
    help = 'Inicializa los grupos de roles básicos en la base de datos'

    def handle(self, *args, **options):
        for role_key, group_name in ROLE_GROUP_MAPPING.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Grupo '{group_name}' creado exitosamente."))
            else:
                self.stdout.write(self.style.WARNING(f"Grupo '{group_name}' ya existía."))

        self.stdout.write(self.style.SUCCESS("Roles y grupos inicializados correctamente."))
