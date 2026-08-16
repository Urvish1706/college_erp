from django.db import models
from django.contrib.auth.models import User


class AuditLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs"
    )

    action = models.CharField(
        max_length=100
    )

    model_name = models.CharField(
        max_length=100,
        blank=True
    )

    object_id = models.CharField(
        max_length=100,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous/System"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {user_str} - {self.action}"


def log_action(user, action, model_name="", object_id="", description="", ip_address=None):
    try:
        user_obj = user if (user and user.is_authenticated) else None
        AuditLog.objects.create(
            user=user_obj,
            action=action,
            model_name=model_name,
            object_id=str(object_id) if object_id else "",
            description=description,
            ip_address=ip_address
        )
    except Exception as e:
        pass
