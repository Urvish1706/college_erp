from django.urls import path
from .views import (
    student_assignments,
    faculty_assignments,
    assignment_list,
)

urlpatterns = [
    path("my-assignments/", student_assignments, name="student_assignments"),
    path("faculty-assignments/", faculty_assignments, name="faculty_assignments"),
    path("list/", assignment_list, name="assignment_list"),
]
