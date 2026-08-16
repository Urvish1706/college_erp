from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from academics.models import Department, Course, Semester


class Notice(models.Model):
    NOTICE_TYPE_CHOICES = [
        ("GENERAL", "General"),
        ("ACADEMIC", "Academic"),
        ("EXAM", "Examination"),
        ("FEE", "Fee & Payment"),
        ("HOLIDAY", "Holiday"),
        ("EVENT", "Event / Function"),
        ("EMERGENCY", "Emergency Alert"),
        ("ASSIGNMENT", "Assignment Notice"),
        ("ATTENDANCE", "Attendance Alert"),
        ("RESULT", "Result Announcement"),
    ]

    PRIORITY_CHOICES = [
        ("NORMAL", "Normal"),
        ("IMPORTANT", "Important"),
        ("URGENT", "Urgent / Critical"),
    ]

    TARGET_AUDIENCE_CHOICES = [
        ("EVERYONE", "Everyone"),
        ("STUDENTS", "Students Only"),
        ("FACULTY", "Faculty Only"),
        ("DEPARTMENT", "Specific Department"),
        ("COURSE", "Specific Course"),
        ("SEMESTER", "Specific Semester"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    notice_type = models.CharField(max_length=30, choices=NOTICE_TYPE_CHOICES, default="GENERAL")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="NORMAL")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_notices")
    publish_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(null=True, blank=True)
    attachment = models.FileField(upload_to="notices/", blank=True, null=True)

    target_audience = models.CharField(max_length=30, choices=TARGET_AUDIENCE_CHOICES, default="EVERYONE")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="notices")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name="notices")
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True, related_name="notices")

    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "-publish_date", "-created_at"]

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False
