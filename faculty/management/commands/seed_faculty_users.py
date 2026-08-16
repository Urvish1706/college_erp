from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from faculty.models import Faculty

from accounts.models import Profile


class Command(BaseCommand):

    help = "Create login accounts for faculty members"

    @transaction.atomic
    def handle(self, *args, **options):

        faculty_members = Faculty.objects.filter(
            is_active=True
        )

        created_count = 0

        for faculty in faculty_members:

            username = faculty.faculty_id.lower()

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": faculty.first_name,
                    "last_name": faculty.last_name,
                    "email": faculty.email,
                }
            )

            # Update user information
            user.first_name = faculty.first_name
            user.last_name = faculty.last_name
            user.email = faculty.email

            # Set password for new users
            if created:
                user.set_password("Faculty@123")
                created_count += 1

            user.save()

            # Connect Faculty with User
            faculty.user = user
            faculty.save(
                update_fields=["user"]
            )

            # Create / update Profile
            profile, _ = Profile.objects.get_or_create(
                user=user
            )

            profile.role = "FACULTY"
            profile.phone = faculty.phone
            profile.save()

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                " Faculty login accounts created!"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Accounts created: {created_count}"
            )
        )

        self.stdout.write("")

        self.stdout.write(
            self.style.WARNING(
                "Username: fac001, fac002, fac003..."
            )
        )

        self.stdout.write(
            self.style.WARNING(
                "Password: Faculty@123"
            )
        )

        self.stdout.write("")