from django.db import models

from students.models import Student
from academics.models import Subject
from faculty.models import Faculty


class Exam(models.Model):

    EXAM_TYPE_CHOICES = [
        ("UNIT_TEST", "Unit Test"),
        ("MIDTERM", "Mid Term"),
        ("INTERNAL", "Internal"),
        ("PRACTICAL", "Practical"),
        ("FINAL", "Final Exam"),
    ]

    name = models.CharField(
        max_length=150
    )

    exam_type = models.CharField(
        max_length=30,
        choices=EXAM_TYPE_CHOICES
    )

    academic_year = models.ForeignKey(
        "academics.AcademicYear",
        on_delete=models.PROTECT,
        related_name="exams"
    )

    semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.PROTECT,
        related_name="exams"
    )

    start_date = models.DateField(
        blank=True,
        null=True
    )

    end_date = models.DateField(
        blank=True,
        null=True
    )

    is_published = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Result(models.Model):

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="results"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="results"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="results"
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
        related_name="entered_results"
    )

    marks_obtained = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    max_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=100
    )

    remarks = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["student", "subject"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "exam",
                    "student",
                    "subject",
                ],
                name="unique_exam_student_subject"
            )
        ]

    @property
    def percentage(self):

        if not self.max_marks:
            return 0

        return round(
            (float(self.marks_obtained) /
             float(self.max_marks)) * 100,
            2
        )

    @property
    def grade(self):

        percentage = self.percentage

        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B+"
        elif percentage >= 60:
            return "B"
        elif percentage >= 50:
            return "C"
        elif percentage >= 40:
            return "D"
        else:
            return "F"

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.subject.name} - "
            f"{self.exam.name}"
        )