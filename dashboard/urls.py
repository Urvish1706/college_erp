from django.urls import path
from .views import (
    dashboard_view,
    student_timetable,
    faculty_timetable,
    reports_view,
)

urlpatterns = [
    path("dashboard/", dashboard_view, name="dashboard"),
    path("timetable/student/", student_timetable, name="student_timetable"),
    path("timetable/faculty/", faculty_timetable, name="faculty_timetable"),
    path("reports/", reports_view, name="reports"),
]