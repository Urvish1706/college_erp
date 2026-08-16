from django.contrib import admin

from .models import (
    AcademicYear,
    Semester,
    Department,
    Course,
    Subject,
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "start_date",
        "end_date",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
    )


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "number",
        "is_active",
    )

    list_filter = (
        "is_active",
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "hod_name",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "code",
        "hod_name",
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "department",
        "duration_years",
        "is_active",
    )

    list_filter = (
        "department",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "code",
        "course",
        "semester",
        "subject_type",
        "credits",
        "is_active",
    )

    list_filter = (
        "course",
        "semester",
        "subject_type",
        "is_active",
    )

    search_fields = (
        "name",
        "code",
    )