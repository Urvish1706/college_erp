from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from results.models import Exam
from students.models import Student
from faculty.models import Faculty


@login_required
def student_exams(request):
    student = Student.objects.filter(user=request.user, is_active=True).first()
    if not student:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard")

    exams = Exam.objects.filter(
        academic_year=student.academic_year,
        semester=student.semester
    ).order_by("-start_date")

    return render(request, "examinations/student_exams.html", {"student": student, "exams": exams})


@login_required
def faculty_exams(request):
    faculty = Faculty.objects.filter(user=request.user, is_active=True).first()
    if not faculty:
        messages.error(request, "Faculty profile not found.")
        return redirect("dashboard")

    exams = Exam.objects.all().order_by("-start_date")
    return render(request, "examinations/faculty_exams.html", {"faculty": faculty, "exams": exams})
