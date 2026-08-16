from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Sets up standard ERP Django Groups and Permissions (Admin, Faculty, Student, Accountant, HOD, Librarian, Exam Cell)"

    def handle(self, *args, **options):
        groups = [
            "Admin",
            "Faculty",
            "Student",
            "Accountant",
            "HOD",
            "Librarian",
            "Exam Cell",
        ]

        created_count = 0
        for g_name in groups:
            group, created = Group.objects.get_or_create(name=g_name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created group: '{g_name}'"))
            else:
                self.stdout.write(f"Group already exists: '{g_name}'")

        self.stdout.write(self.style.SUCCESS(f"ERP Groups setup completed. ({created_count} new groups created)"))
