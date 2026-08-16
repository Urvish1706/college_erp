from django.db import models
from django.utils import timezone


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.PROTECT,
        related_name="assignments"
    )

    faculty = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.PROTECT,
        related_name="assignments"
    )

    course = models.ForeignKey(
        "academics.Course",
        on_delete=models.PROTECT,
        related_name="assignments"
    )

    semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.PROTECT,
        related_name="assignments"
    )

    academic_year = models.ForeignKey(
        "academics.AcademicYear",
        on_delete=models.PROTECT,
        related_name="assignments"
    )

    attachment = models.FileField(
        upload_to="assignments/",
        blank=True,
        null=True
    )

    assigned_date = models.DateField(default=timezone.now)
    due_date = models.DateTimeField()
    max_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=100.00
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-due_date", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

    @property
    def is_overdue(self):
        return timezone.now() > self.due_date

    @property
    def is_due_soon(self):
        now = timezone.now()
        if now > self.due_date:
            return False
        return (self.due_date - now).total_seconds() <= 86400 * 2

    @property
    def computed_status(self):
        if not self.is_active:
            return "Closed"
        now = timezone.now()
        if now > self.due_date:
            return "Overdue"
        elif (self.due_date - now).total_seconds() <= 86400 * 2:
            return "Due Soon"
        elif now.date() < self.assigned_date:
            return "Upcoming"
        else:
            return "Active"


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUBMITTED", "Submitted"),
        ("LATE", "Late"),
        ("GRADED", "Graded"),
        ("RETURNED", "Returned"),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.PROTECT,
        related_name="assignment_submissions"
    )

    submission_file = models.FileField(
        upload_to="assignments/submissions/",
        blank=True,
        null=True
    )

    submission_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    feedback = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SUBMITTED"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "student"],
                name="unique_assignment_student_submission"
            )
        ]

    def __str__(self):
        return f"{self.student.student_id} - {self.assignment.title}"

    @property
    def percentage(self):
        if self.marks is None or not self.assignment.max_marks:
            return 0
        return round((float(self.marks) / float(self.assignment.max_marks)) * 100, 2)
