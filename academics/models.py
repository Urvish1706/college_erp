from django.db import models


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class Semester(models.Model):
    name = models.CharField(max_length=50)
    number = models.PositiveIntegerField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    hod_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True)
    duration_years = models.PositiveIntegerField(default=4)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Subject(models.Model):

    SUBJECT_TYPES = [
        ("THEORY", "Theory"),
        ("PRACTICAL", "Practical"),
        ("LAB", "Lab"),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True)
    credits = models.PositiveIntegerField(default=3)

    subject_type = models.CharField(
        max_length=20,
        choices=SUBJECT_TYPES,
        default="THEORY"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"