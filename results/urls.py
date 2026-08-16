from django.urls import path
from .views import (
    result_entry,
    student_results,
    exam_list,
    toggle_publish,
)


urlpatterns = [
    path(
        "entry/",
        result_entry,
        name="result_entry"
    ),
    path(
        "my-results/",
        student_results,
        name="student_results"
    ),
    path(
        "exams/",
        exam_list,
        name="results_exam_list"
    ),
    path(
        "exams/<int:exam_id>/toggle-publish/",
        toggle_publish,
        name="toggle_publish"
    ),
]