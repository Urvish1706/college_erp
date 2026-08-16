from django.urls import path

from .views import (
    student_list,
    student_create,
    student_update,
    student_delete,
    student_detail,
    attendance_report,
)


urlpatterns = [

    path(
        "students/",
        student_list,
        name="student_list"
    ),

    path(
        "students/add/",
        student_create,
        name="student_create"
    ),

    path(
        "students/<int:pk>/",
        student_detail,
        name="student_detail"
    ),

    path(
        "students/<int:pk>/edit/",
        student_update,
        name="student_update"
    ),

    path(
        "students/<int:pk>/delete/",
        student_delete,
        name="student_delete"
    ),

    path(
        "attendance-report/",
        attendance_report,
        name="attendance_report"
    ),

]