from django.db import models
from django.utils import timezone


class ExamSchedule(models.Model):
    exam = models.ForeignKey(
        "results.Exam",
        on_delete=models.CASCADE,
        related_name="schedules"
    )

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.PROTECT,
        related_name="exam_schedules"
    )

    course = models.ForeignKey(
        "academics.Course",
        on_delete=models.PROTECT,
        related_name="exam_schedules"
    )

    semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.PROTECT,
        related_name="exam_schedules"
    )

    academic_year = models.ForeignKey(
        "academics.AcademicYear",
        on_delete=models.PROTECT,
        related_name="exam_schedules"
    )

    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    room = models.CharField(
        max_length=100,
        blank=True
    )

    faculty = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="invigilation_schedules",
        verbose_name="Invigilator"
    )

    max_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=100.00
    )

    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["exam_date", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "subject", "course", "semester", "exam_date"],
                name="unique_exam_schedule"
            )
        ]

    def __str__(self):
        return f"{self.exam.name} - {self.subject.name} ({self.exam_date})"

    @property
    def computed_status(self):
        if not self.is_active:
            return "Inactive"
        now = timezone.now()
        today = now.date()

        if self.exam_date < today:
            return "Completed"
        elif self.exam_date == today:
            current_time = now.time()
            if current_time > self.end_time:
                return "Completed"
            elif current_time >= self.start_time:
                return "Ongoing"
            else:
                return "Today"
        else:
            return "Upcoming"
