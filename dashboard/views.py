from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Count, Q

from students.models import Student
from faculty.models import Faculty
from academics.models import Department, Course, Subject
from results.models import Exam, Result


@login_required
def dashboard_view(request):

    user = request.user

    # ==========================================
    # DETERMINE USER ROLE
    # ==========================================

    if user.is_superuser:
        role = "ADMIN"
    elif hasattr(user, "faculty_profile") or (hasattr(user, "profile") and user.profile.is_faculty):
        role = "FACULTY"
    elif hasattr(user, "profile"):
        role = user.profile.role
    else:
        role = "STUDENT"

    # Redirect Faculty to Faculty Dashboard
    if role == "FACULTY":
        return redirect("faculty_dashboard")

    # ==========================================
    # COMMON DASHBOARD DATA
    # ==========================================

    context = {
        "role": role,
        "total_students": Student.objects.filter(is_active=True).count(),
        "total_faculty": Faculty.objects.filter(is_active=True).count(),
        "total_departments": Department.objects.filter(is_active=True).count(),
        "total_courses": Course.objects.filter(is_active=True).count(),
        "total_subjects": Subject.objects.filter(is_active=True).count(),
        "total_exams": Exam.objects.count(),
        "published_exams": Exam.objects.filter(is_published=True).count(),
    }

    # ==========================================
    # STUDENT DASHBOARD
    # ==========================================

    if role == "STUDENT":

        student = (
            Student.objects
            .filter(
                user=user,
                is_active=True
            )
            .select_related(
                "department",
                "course",
                "semester",
                "academic_year",
            )
            .first()
        )

        context["student"] = student

        if student:
            attendance = (
                student.attendance_records
                .aggregate(
                    total=Count("id"),
                    present=Count(
                        "id",
                        filter=Q(status="PRESENT")
                    )
                )
            )

            total = attendance["total"] or 0
            present = attendance["present"] or 0

            if total > 0:
                attendance_percentage = round((present / total) * 100, 2)
            else:
                attendance_percentage = 0

            context["attendance_percentage"] = attendance_percentage
            context["attendance_total"] = total
            context["attendance_present"] = present

            # Latest Published Result
            latest_result = (
                Result.objects.filter(
                    student=student,
                    exam__is_published=True
                )
                .select_related("exam", "subject")
                .order_by("-exam__created_at")
                .first()
            )
            context["latest_result"] = latest_result

        else:
            context["attendance_percentage"] = 0

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )


@login_required
def student_timetable(request):
    student = Student.objects.filter(user=request.user, is_active=True).first()
    return render(request, "dashboard/student_timetable.html", {"student": student})


@login_required
def faculty_timetable(request):
    faculty = Faculty.objects.filter(user=request.user, is_active=True).first()
    return render(request, "dashboard/faculty_timetable.html", {"faculty": faculty})


@login_required
def reports_view(request):
    return render(request, "dashboard/reports.html")