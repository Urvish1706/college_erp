from django.contrib import admin
from .models import Faculty, FacultySubjectAssignment
from .models import Faculty


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):

    list_display = (
        "faculty_id",
        "full_name",
        "email",
        "department",
        "qualification",
        "experience_years",
        "is_active",
    )

    list_filter = (
        "department",
        "is_active",
    )

    search_fields = (
        "faculty_id",
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

@admin.register(FacultySubjectAssignment)
class FacultySubjectAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "faculty",
        "subject",
        "assigned_at",
        "is_active",
    )

    list_filter = (
        "is_active",
        "subject__semester",
        "subject__course",
    )

    search_fields = (
        "faculty__faculty_id",
        "faculty__first_name",
        "faculty__last_name",
        "subject__name",
        "subject__code",
    )