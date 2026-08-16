from django.contrib import admin
from .models import ExamSchedule


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "exam",
        "subject",
        "course",
        "semester",
        "exam_date",
        "start_time",
        "end_time",
        "room",
        "faculty",
        "max_marks",
        "is_active",
    ]

    list_filter = [
        "exam",
        "subject",
        "course",
        "semester",
        "faculty",
        "exam_date",
        "is_active",
    ]

    search_fields = [
        "exam__name",
        "subject__name",
        "subject__code",
        "room",
        "faculty__first_name",
        "faculty__last_name",
    ]
