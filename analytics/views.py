import csv
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum, Avg, Max, Min
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from students.models import Student
from faculty.models import Faculty, FacultySubjectAssignment
from academics.models import Department, Course, Semester, AcademicYear, Subject
from results.models import Exam, Result
from fees.models import Fee, FeePayment
from attendance.models import Attendance
from assignments.models import Assignment, AssignmentSubmission
from complaints.models import Complaint
from leave_management.models import LeaveApplication


def is_admin_or_staff(user):
    return user.is_superuser or user.is_staff or (hasattr(user, "profile") and user.profile.role in ["ADMIN", "HOD", "ACCOUNTANT", "EXAM_CELL"])


@login_required
def analytics_dashboard(request):
    user = request.user
    if hasattr(user, "faculty_profile") and not is_admin_or_staff(user):
        return redirect("faculty_analytics")
    elif hasattr(user, "student_profile") and not is_admin_or_staff(user):
        return redirect("student_analytics")

    if not is_admin_or_staff(user):
        raise PermissionDenied("You are not authorized to view global institutional analytics.")

    # Overview KPIs
    active_students_count = Student.objects.filter(is_active=True).count()
    faculty_count = Faculty.objects.filter(is_active=True).count()
    course_count = Course.objects.filter(is_active=True).count()
    subject_count = Subject.objects.filter(is_active=True).count()
    department_count = Department.objects.filter(is_active=True).count()
    exam_count = Exam.objects.count()
    published_exam_count = Exam.objects.filter(is_published=True).count()

    total_fees_billed = Fee.objects.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
    total_fees_collected = FeePayment.objects.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    total_fees_pending = max(Decimal("0.00"), total_fees_billed - total_fees_collected)

    open_complaints_count = Complaint.objects.filter(status__in=["OPEN", "IN_PROGRESS"]).count()
    pending_leaves_count = LeaveApplication.objects.filter(status="PENDING").count()

    # Filters
    academic_year_id = request.GET.get("academic_year")
    semester_id = request.GET.get("semester")
    department_id = request.GET.get("department")

    students_qs = Student.objects.filter(is_active=True)
    if academic_year_id:
        students_qs = students_qs.filter(academic_year_id=academic_year_id)
    if semester_id:
        students_qs = students_qs.filter(semester_id=semester_id)
    if department_id:
        students_qs = students_qs.filter(department_id=department_id)

    # Attendance Warning List (< 75%)
    low_attendance_students = []
    for s in students_qs.select_related("course", "semester", "department")[:300]:
        att = s.attendance_records.aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status="PRESENT"))
        )
        total_cls = att["total"] or 0
        pres_cls = att["present"] or 0
        pct = round((pres_cls / total_cls) * 100, 2) if total_cls > 0 else 100.0

        if pct < 75.0:
            category = "Critical" if pct < 60.0 else "Warning"
            low_attendance_students.append({
                "student": s,
                "total_classes": total_cls,
                "present_classes": pres_cls,
                "percentage": pct,
                "category": category,
            })

    low_attendance_students.sort(key=lambda x: x["percentage"])

    # Result Stats (Published Only)
    results_qs = Result.objects.filter(exam__is_published=True)
    res_stats = results_qs.aggregate(
        avg_marks=Avg("marks_obtained"),
        max_marks=Max("marks_obtained"),
        min_marks=Min("marks_obtained"),
        total_count=Count("id")
    )

    # Fee Stats Breakdown
    fees_qs = Fee.objects.select_related("student")
    paid_students_count = 0
    partial_students_count = 0
    unpaid_students_count = 0
    for f in fees_qs:
        st = f.computed_status
        if st == "PAID":
            paid_students_count += 1
        elif st == "PARTIAL":
            partial_students_count += 1
        else:
            unpaid_students_count += 1

    # Assignments Stats
    total_assignments = Assignment.objects.count()
    total_submissions = AssignmentSubmission.objects.count()

    context = {
        "active_students_count": active_students_count,
        "faculty_count": faculty_count,
        "course_count": course_count,
        "subject_count": subject_count,
        "department_count": department_count,
        "exam_count": exam_count,
        "published_exam_count": published_exam_count,
        "total_fees_billed": total_fees_billed,
        "total_fees_collected": total_fees_collected,
        "total_fees_pending": total_fees_pending,
        "open_complaints_count": open_complaints_count,
        "pending_leaves_count": pending_leaves_count,
        "low_attendance_students": low_attendance_students[:50],
        "res_stats": res_stats,
        "paid_students_count": paid_students_count,
        "partial_students_count": partial_students_count,
        "unpaid_students_count": unpaid_students_count,
        "total_assignments": total_assignments,
        "total_submissions": total_submissions,
        "academic_years": AcademicYear.objects.all(),
        "semesters": Semester.objects.all(),
        "departments": Department.objects.all(),
        "selected_ay": academic_year_id,
        "selected_sem": semester_id,
        "selected_dept": department_id,
    }
    return render(request, "analytics/admin_analytics.html", context)


@login_required
def faculty_analytics(request):
    faculty = getattr(request.user, "faculty_profile", None)
    if not faculty:
        faculty = Faculty.objects.filter(user=request.user, is_active=True).first()

    if not faculty:
        messages.error(request, "Faculty profile not found.")
        return redirect("dashboard")

    assigned_subjects = Subject.objects.filter(
        faculty_assignments__faculty=faculty,
        faculty_assignments__is_active=True,
        is_active=True
    ).select_related("course", "semester").distinct()

    subject_analytics = []
    for sub in assigned_subjects:
        att = Attendance.objects.filter(subject=sub, faculty=faculty).aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status="PRESENT"))
        )
        tot = att["total"] or 0
        pres = att["present"] or 0
        att_pct = round((pres / tot) * 100, 2) if tot > 0 else 0.0

        res_avg = Result.objects.filter(subject=sub, faculty=faculty, exam__is_published=True).aggregate(
            avg=Avg("marks_obtained")
        )["avg"] or 0.0

        assignments_cnt = Assignment.objects.filter(subject=sub, faculty=faculty).count()
        submissions_cnt = AssignmentSubmission.objects.filter(assignment__subject=sub, assignment__faculty=faculty).count()

        subject_analytics.append({
            "subject": sub,
            "total_classes": tot,
            "present_classes": pres,
            "attendance_pct": att_pct,
            "average_marks": round(float(res_avg), 2),
            "assignments_count": assignments_cnt,
            "submissions_count": submissions_cnt,
        })

    context = {
        "faculty": faculty,
        "subject_analytics": subject_analytics,
        "total_subjects": assigned_subjects.count(),
    }
    return render(request, "analytics/faculty_analytics.html", context)


@login_required
def student_analytics(request):
    student = getattr(request.user, "student_profile", None)
    if not student:
        student = Student.objects.filter(user=request.user, is_active=True).first()

    if not student:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard")

    # Attendance Summary
    att_stats = Attendance.objects.filter(student=student).aggregate(
        total=Count("id"),
        present=Count("id", filter=Q(status="PRESENT"))
    )
    tot = att_stats["total"] or 0
    pres = att_stats["present"] or 0
    overall_att_pct = round((pres / tot) * 100, 2) if tot > 0 else 0.0

    # Results Summary
    results = Result.objects.filter(student=student, exam__is_published=True).select_related("exam", "subject")

    # Fee Summary
    fees = Fee.objects.filter(student=student)
    total_fee_amount = fees.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
    total_fee_paid = FeePayment.objects.filter(fee__student=student).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    pending_fee_amount = max(Decimal("0.00"), total_fee_amount - total_fee_paid)

    # Assignments Summary
    submitted_assignments = AssignmentSubmission.objects.filter(student=student).count()

    context = {
        "student": student,
        "overall_att_pct": overall_att_pct,
        "total_classes": tot,
        "present_classes": pres,
        "results": results,
        "total_fee_amount": total_fee_amount,
        "total_fee_paid": total_fee_paid,
        "pending_fee_amount": pending_fee_amount,
        "submitted_assignments": submitted_assignments,
    }
    return render(request, "analytics/student_analytics.html", context)


@login_required
def analytics_export_excel(request):
    if not is_admin_or_staff(request.user):
        raise PermissionDenied("Unauthorized to export analytical data.")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="analytics_report.csv"'

    writer = csv.writer(response)
    writer.writerow(["Student ID", "Student Name", "Course", "Semester", "Total Classes", "Present Classes", "Attendance %", "Warning Status"])

    students_qs = Student.objects.filter(is_active=True).select_related("course", "semester")
    for s in students_qs:
        att = s.attendance_records.aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status="PRESENT"))
        )
        tot = att["total"] or 0
        pres = att["present"] or 0
        pct = round((pres / tot) * 100, 2) if tot > 0 else 100.0
        status = "Critical (<60%)" if pct < 60.0 else ("Warning (60-75%)" if pct < 75.0 else "Safe (75%+)")

        writer.writerow([s.student_id, s.full_name, s.course.name if s.course else "", s.semester.name if s.semester else "", tot, pres, f"{pct:.2f}%", status])

    return response


@login_required
def analytics_print_report(request):
    if not is_admin_or_staff(request.user):
        raise PermissionDenied("Unauthorized to print institutional analytics.")

    context = {
        "active_students_count": Student.objects.filter(is_active=True).count(),
        "faculty_count": Faculty.objects.filter(is_active=True).count(),
        "course_count": Course.objects.filter(is_active=True).count(),
        "total_fees_billed": Fee.objects.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00"),
        "total_fees_collected": FeePayment.objects.aggregate(total=Sum("amount"))["total"] or Decimal("0.00"),
        "generated_date": timezone.now(),
    }
    return render(request, "analytics/print_report.html", context)
