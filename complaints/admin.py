from django.contrib import admin
from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "category", "priority", "status", "created_at")
    list_filter = ("category", "priority", "status", "created_at")
    search_fields = ("user__username", "subject", "description")
