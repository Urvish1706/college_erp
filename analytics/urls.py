from django.urls import path
from .views import (
    analytics_dashboard,
    faculty_analytics,
    student_analytics,
    analytics_export_excel,
    analytics_print_report,
)

urlpatterns = [
    path("", analytics_dashboard, name="analytics_dashboard"),
    path("faculty/", faculty_analytics, name="faculty_analytics"),
    path("student/", student_analytics, name="student_analytics"),
    path("export/excel/", analytics_export_excel, name="analytics_export_excel"),
    path("export/print/", analytics_print_report, name="analytics_print_report"),
]
