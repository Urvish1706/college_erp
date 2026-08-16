from django.contrib import admin

from .models import Exam, Result


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "exam_type",
        "academic_year",
        "semester",
        "start_date",
        "end_date",
        "is_published",
        "is_active",
        "created_at",
    )

    list_filter = (
        "exam_type",
        "academic_year",
        "semester",
        "is_published",
        "is_active",
    )

    search_fields = (
        "name",
    )


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):

    list_display = (
        "exam",
        "student",
        "subject",
        "faculty",
        "marks_obtained",
        "max_marks",
    )

    list_filter = (
        "exam",
        "subject",
        "faculty",
    )

    search_fields = (
        "student__student_id",
        "student__first_name",
        "student__last_name",
        "subject__name",
    )