from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "student_id",
        "full_name",
        "email",
        "department",
        "course",
        "semester",
        "academic_year",
        "is_active",
    )

    list_filter = (
        "department",
        "course",
        "semester",
        "academic_year",
        "is_active",
    )

    search_fields = (
        "student_id",
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    readonly_fields = (
        "admission_date",
        "created_at",
        "updated_at",
    )