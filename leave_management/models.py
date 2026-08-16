from django.db import models
from django.contrib.auth.models import User


class LeaveApplication(models.Model):
    LEAVE_TYPE_CHOICES = [
        ("CASUAL", "Casual Leave"),
        ("SICK", "Medical / Sick Leave"),
        ("ACADEMIC", "Academic / Seminar Leave"),
        ("EMERGENCY", "Emergency Leave"),
        ("OTHER", "Other"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending Review"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_applications")
    leave_type = models.CharField(max_length=30, choices=LEAVE_TYPE_CHOICES, default="CASUAL")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    review_remarks = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_leaves")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.applicant.username} - {self.get_leave_type_display()} ({self.get_status_display()})"
