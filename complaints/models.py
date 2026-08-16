from django.db import models
from django.contrib.auth.models import User


class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ("ACADEMIC", "Academic Grievance"),
        ("HOSTEL", "Hostel & Maintenance"),
        ("INFRASTRUCTURE", "Campus Infrastructure"),
        ("ANTI_RAGGING", "Anti-Ragging / Bullying"),
        ("FINANCE", "Fee & Finance Issue"),
        ("OTHER", "Other Complaint"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("URGENT", "Urgent / Critical"),
    ]

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
        ("REJECTED", "Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complaints")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="ACADEMIC")
    subject = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.FileField(upload_to="complaints/", blank=True, null=True)

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="MEDIUM")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="OPEN")
    admin_response = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.get_status_display()})"
