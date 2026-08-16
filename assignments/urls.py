from django.urls import path
from .views import (
    student_assignments,
    faculty_assignments,
    assignment_list,
    assignment_detail,
    assignment_create,
    assignment_update,
    assignment_delete,
    submit_assignment,
    my_submission,
    submission_list,
    grade_submission,
)

urlpatterns = [
    path("my-assignments/", student_assignments, name="student_assignments"),
    path("faculty-assignments/", faculty_assignments, name="faculty_assignments"),
    path("list/", assignment_list, name="assignment_list"),
    path("create/", assignment_create, name="assignment_create"),
    path("<int:pk>/", assignment_detail, name="assignment_detail"),
    path("<int:pk>/edit/", assignment_update, name="assignment_update"),
    path("<int:pk>/delete/", assignment_delete, name="assignment_delete"),
    path("<int:pk>/submit/", submit_assignment, name="submit_assignment"),
    path("<int:pk>/submissions/", submission_list, name="submission_list"),
    path("submission/<int:pk>/", my_submission, name="my_submission"),
    path("submission/<int:pk>/grade/", grade_submission, name="grade_submission"),
]
