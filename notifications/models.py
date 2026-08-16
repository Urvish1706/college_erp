from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ("ASSIGNMENT", "Assignment"),
        ("EXAM", "Examination"),
        ("RESULT", "Result"),
        ("FEE", "Fee & Payment"),
        ("ATTENDANCE", "Attendance"),
        ("NOTICE", "Notice / Announcement"),
        ("SYSTEM", "System Alert"),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES,
        default="SYSTEM"
    )

    related_url = models.CharField(
        max_length=255,
        blank=True
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient.username} - {self.title} ({'Read' if self.is_read else 'Unread'})"


def create_notification(recipient, title, message, notification_type="SYSTEM", related_url=""):
    if recipient:
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            related_url=related_url
        )
    return None
