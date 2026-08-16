from django.urls import path

from .views import (
    mark_attendance,
    attendance_history,
    student_attendance,
)


urlpatterns = [

    # Faculty
    path(
        "attendance/mark/",
        mark_attendance,
        name="mark_attendance"
    ),

    path(
        "attendance/history/",
        attendance_history,
        name="attendance_history"
    ),

    # Student
    path(
        "attendance/my-attendance/",
        student_attendance,
        name="student_attendance"
    ),

]