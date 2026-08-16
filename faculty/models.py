from django.db import models
from django.contrib.auth.models import User

from academics.models import Department


class Faculty(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="faculty_profile",
        blank=True,
        null=True,
    )

    faculty_id = models.CharField(
        max_length=30,
        unique=True
    )

    profile_photo = models.ImageField(
        upload_to="faculty/",
        blank=True,
        null=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    qualification = models.CharField(
        max_length=200,
        blank=True
    )

    experience_years = models.PositiveIntegerField(
        default=0
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="faculty_members"
    )

    joining_date = models.DateField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["faculty_id"]

    def __str__(self):
        return f"{self.faculty_id} - {self.full_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

class FacultySubjectAssignment(models.Model):

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name="subject_assignments"
    )

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="faculty_assignments"
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["-assigned_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["faculty", "subject"],
                name="unique_faculty_subject"
            )
        ]

    def __str__(self):
        return (
            f"{self.faculty.full_name} → "
            f"{self.subject.name}"
        )