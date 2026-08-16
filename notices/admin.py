from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "notice_type", "priority", "target_audience", "publish_date", "is_published")
    list_filter = ("notice_type", "priority", "target_audience", "is_published", "publish_date")
    search_fields = ("title", "content")
