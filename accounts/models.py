from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    ROLE_CHOICES = [
        ("ADMIN", "Administrator"),
        ("FACULTY", "Faculty"),
        ("STUDENT", "Student"),
        ("ACCOUNTANT", "Accountant"),
        ("STAFF", "Staff"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="STUDENT"
    )

    profile_photo = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    @property
    def is_admin(self):
        return self.role == "ADMIN" or self.user.is_superuser

    @property
    def is_faculty(self):
        return self.role == "FACULTY"

    @property
    def is_student(self):
        return self.role == "STUDENT"

    @property
    def is_accountant(self):
        return self.role == "ACCOUNTANT"

    @property
    def is_staff_member(self):
        return self.role == "STAFF"