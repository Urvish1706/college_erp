from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Department, Course, AcademicYear, Semester, Subject


@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, "academics/department_list.html", {"departments": departments})


@login_required
def course_list(request):
    courses = Course.objects.select_related("department").all()
    return render(request, "academics/course_list.html", {"courses": courses})


@login_required
def academic_year_list(request):
    years = AcademicYear.objects.all()
    return render(request, "academics/academic_year_list.html", {"years": years})


@login_required
def semester_list(request):
    semesters = Semester.objects.all()
    return render(request, "academics/semester_list.html", {"semesters": semesters})


@login_required
def subject_list(request):
    subjects = Subject.objects.select_related("course", "semester").all()
    return render(request, "academics/subject_list.html", {"subjects": subjects})
