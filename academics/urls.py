from django.urls import path
from .views import (
    department_list,
    course_list,
    academic_year_list,
    semester_list,
    subject_list,
)

urlpatterns = [
    path("departments/", department_list, name="department_list"),
    path("courses/", course_list, name="course_list"),
    path("academic-years/", academic_year_list, name="academic_year_list"),
    path("semesters/", semester_list, name="semester_list"),
    path("subjects/", subject_list, name="subject_list"),
]
