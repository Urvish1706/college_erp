from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "subject",
        "faculty",
        "date",
        "status",
    )

    list_filter = (
        "status",
        "date",
        "subject",
        "faculty",
    )

    search_fields = (
        "student__student_id",
        "student__first_name",
        "student__last_name",
        "subject__name",
        "subject__code",
        "faculty__first_name",
        "faculty__last_name",
    )

    date_hierarchy = "date"