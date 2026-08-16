from django.urls import path
from .views import student_exams, faculty_exams

urlpatterns = [
    path("my-exams/", student_exams, name="student_exams"),
    path("faculty-exams/", faculty_exams, name="faculty_exams"),
]
