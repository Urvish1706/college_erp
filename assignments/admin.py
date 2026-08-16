from django.contrib import admin
from .models import Assignment, AssignmentSubmission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "subject",
        "faculty",
        "course",
        "semester",
        "assigned_date",
        "due_date",
        "max_marks",
        "is_active",
    ]

    list_filter = [
        "subject",
        "faculty",
        "course",
        "semester",
        "is_active",
        "academic_year",
    ]

    search_fields = [
        "title",
        "subject__name",
        "faculty__first_name",
        "faculty__last_name",
        "course__name",
    ]

    date_hierarchy = "due_date"


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "assignment",
        "student",
        "submitted_at",
        "status",
        "marks",
    ]

    list_filter = [
        "status",
        "assignment__subject",
        "submitted_at",
    ]

    search_fields = [
        "student__student_id",
        "student__first_name",
        "student__last_name",
        "assignment__title",
    ]
