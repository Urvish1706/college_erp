from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "model_name", "object_id", "ip_address")
    list_filter = ("action", "model_name", "created_at")
    search_fields = ("user__username", "action", "description", "ip_address")
    readonly_fields = ("user", "action", "model_name", "object_id", "description", "ip_address", "created_at")
