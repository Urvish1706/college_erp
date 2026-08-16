from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from students.models import Student
from faculty.models import Faculty, FacultySubjectAssignment


@login_required
def student_assignments(request):
    student = Student.objects.filter(user=request.user, is_active=True).first()
    if not student:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard")

    return render(request, "assignments/student_assignments.html", {"student": student})


@login_required
def faculty_assignments(request):
    faculty = Faculty.objects.filter(user=request.user, is_active=True).first()
    if not faculty:
        messages.error(request, "Faculty profile not found.")
        return redirect("dashboard")

    assignments = FacultySubjectAssignment.objects.filter(faculty=faculty, is_active=True).select_related("subject")
    return render(request, "assignments/faculty_assignments.html", {"faculty": faculty, "assignments": assignments})


@login_required
def assignment_list(request):
    return render(request, "assignments/assignment_list.html")
