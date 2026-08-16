import csv
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Count, Q, Sum
from django.http import HttpResponse

from students.models import Student
from faculty.models import Faculty
from academics.models import Department, Course, Subject
from results.models import Exam, Result
from fees.models import Fee, FeePayment
from attendance.models import Attendance


@login_required
def dashboard_view(request):
    user = request.user

    if user.is_superuser:
        role = "ADMIN"
    elif hasattr(user, "faculty_profile") or (hasattr(user, "profile") and user.profile.is_faculty):
        role = "FACULTY"
    elif hasattr(user, "profile"):
        role = user.profile.role
    else:
        role = "STUDENT"

    if role == "FACULTY":
        return redirect("faculty_dashboard")

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

    if role == "STUDENT":
        student = (
            Student.objects
            .filter(user=user, is_active=True)
            .select_related("department", "course", "semester", "academic_year")
            .first()
        )
        context["student"] = student

        if student:
            attendance = (
                student.attendance_records
                .aggregate(
                    total=Count("id"),
                    present=Count("id", filter=Q(status="PRESENT"))
                )
            )
            total = attendance["total"] or 0
            present = attendance["present"] or 0
            attendance_percentage = round((present / total) * 100, 2) if total > 0 else 0

            context["attendance_percentage"] = attendance_percentage
            context["attendance_total"] = total
            context["attendance_present"] = present

            latest_result = (
                Result.objects.filter(student=student, exam__is_published=True)
                .select_related("exam", "subject")
                .order_by("-exam__created_at")
                .first()
            )
            context["latest_result"] = latest_result
        else:
            context["attendance_percentage"] = 0

    return render(request, "dashboard/dashboard.html", context)


@login_required
def student_timetable(request):
    student = Student.objects.filter(user=request.user, is_active=True).first()
    return render(request, "dashboard/student_timetable.html", {"student": student})


@login_required
def faculty_timetable(request):
    faculty = Faculty.objects.filter(user=request.user, is_active=True).first()
    return render(request, "dashboard/faculty_timetable.html", {"faculty": faculty})


from django.core.exceptions import PermissionDenied


@login_required
def reports_view(request):
    user = request.user
    is_admin_or_staff = user.is_superuser or user.is_staff or (hasattr(user, "profile") and user.profile.role in ["ADMIN", "HOD", "ACCOUNTANT"])
    if not is_admin_or_staff:
        raise PermissionDenied("You are not authorized to access institutional reports.")

    report_type = request.GET.get("export")
    if report_type:
        response = HttpResponse(content_type="text/csv")
        if report_type == "students":
            response["Content-Disposition"] = 'attachment; filename="students_report.csv"'
            writer = csv.writer(response)
            writer.writerow(["Student ID", "First Name", "Last Name", "Email", "Department", "Course", "Semester", "Status"])
            for s in Student.objects.select_related("department", "course", "semester").all():
                writer.writerow([s.student_id, s.first_name, s.last_name, s.user.email if s.user else "", s.department.name if s.department else "", s.course.name if s.course else "", s.semester.number if s.semester else "", "Active" if s.is_active else "Inactive"])
            return response

        elif report_type == "fees":
            response["Content-Disposition"] = 'attachment; filename="fees_report.csv"'
            writer = csv.writer(response)
            writer.writerow(["Student ID", "Student Name", "Fee Type", "Total Amount", "Total Paid", "Pending Amount", "Status"])
            for f in Fee.objects.select_related("student").all():
                writer.writerow([f.student.student_id, f.student.full_name, f.get_fee_type_display(), f"{f.total_amount:.2f}", f"{f.total_paid:.2f}", f"{f.pending_amount:.2f}", f.computed_status])
            return response

        elif report_type == "attendance":
            response["Content-Disposition"] = 'attachment; filename="attendance_report.csv"'
            writer = csv.writer(response)
            writer.writerow(["Student ID", "Student Name", "Subject", "Date", "Status"])
            for a in Attendance.objects.select_related("student", "subject")[:5000]:
                writer.writerow([a.student.student_id, a.student.full_name, a.subject.name, a.date, a.get_status_display()])
            return response

    context = {
        "active_students_count": Student.objects.filter(is_active=True).count(),
        "total_fees_billed": Fee.objects.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00"),
        "total_payments_collected": FeePayment.objects.aggregate(total=Sum("amount"))["total"] or Decimal("0.00"),
    }
    return render(request, "dashboard/reports.html", context)