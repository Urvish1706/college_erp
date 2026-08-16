from django.urls import path
from .views import (
    exam_list,
    exam_detail,
    exam_create,
    exam_update,
    exam_delete,
    exam_toggle_publish,
    schedule_create,
    schedule_update,
    schedule_delete,
    schedule_detail,
    student_exams,
    faculty_exams,
)

urlpatterns = [
    path("list/", exam_list, name="exam_list"),
    path("my-exams/", student_exams, name="student_exams"),
    path("faculty-exams/", faculty_exams, name="faculty_exams"),
    path("faculty/", faculty_exams),
    path("create/", exam_create, name="exam_create"),
    path("<int:pk>/", exam_detail, name="exam_detail"),
    path("<int:pk>/edit/", exam_update, name="exam_update"),
    path("<int:pk>/delete/", exam_delete, name="exam_delete"),
    path("<int:pk>/toggle-publish/", exam_toggle_publish, name="exam_toggle_publish"),
    path("<int:exam_pk>/schedules/create/", schedule_create, name="schedule_create"),
    path("schedules/<int:pk>/", schedule_detail, name="schedule_detail"),
    path("schedules/<int:pk>/edit/", schedule_update, name="schedule_update"),
    path("schedules/<int:pk>/delete/", schedule_delete, name="schedule_delete"),
]
