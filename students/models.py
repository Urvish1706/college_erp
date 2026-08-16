from django.db import models
from django.contrib.auth.models import User

from academics.models import (
    Department,
    Course,
    AcademicYear,
    Semester,
)


class Student(models.Model):

    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile",
        blank=True,
        null=True,
    )

    student_id = models.CharField(
        max_length=30,
        unique=True
    )

    profile_photo = models.ImageField(
        upload_to="students/",
        blank=True,
        null=True
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    guardian_name = models.CharField(
        max_length=150,
        blank=True
    )

    guardian_phone = models.CharField(
        max_length=15,
        blank=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="students"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="students"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.PROTECT,
        related_name="students"
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
        related_name="students"
    )

    admission_date = models.DateField(
        auto_now_add=True
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
        ordering = ["student_id"]

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()