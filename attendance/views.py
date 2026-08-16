from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q

from faculty.models import Faculty, FacultySubjectAssignment
from students.models import Student
from academics.models import Subject

from .models import Attendance


# =========================================================
# FACULTY - MARK ATTENDANCE
# =========================================================

@login_required
def mark_attendance(request):

    # -----------------------------------------------------
    # Check Faculty Login
    # -----------------------------------------------------

    try:
        faculty = request.user.faculty_profile

    except Faculty.DoesNotExist:

        messages.error(
            request,
            "Only Faculty can access attendance management."
        )

        return redirect("dashboard")


    # -----------------------------------------------------
    # Faculty Active Check
    # -----------------------------------------------------

    if not faculty.is_active:

        messages.error(
            request,
            "Your Faculty account is inactive."
        )

        return redirect("faculty_login")


    # -----------------------------------------------------
    # Get only Faculty assigned subjects
    # -----------------------------------------------------

    assignments = (
        FacultySubjectAssignment.objects
        .filter(
            faculty=faculty,
            is_active=True
        )
        .select_related("subject")
    )


    subjects = [
        assignment.subject
        for assignment in assignments
    ]


    # -----------------------------------------------------
    # Selected Subject
    # -----------------------------------------------------

    selected_subject_id = request.GET.get(
        "subject"
    )


    selected_date = request.GET.get(
        "date"
    )


    if not selected_date:

        selected_date = date.today().isoformat()


    selected_subject = None

    students = Student.objects.none()


    # =====================================================
    # LOAD STUDENTS
    # =====================================================

    if selected_subject_id:

        # Check that subject belongs to this Faculty

        selected_subject = next(
            (
                subject
                for subject in subjects
                if str(subject.id) == str(
                    selected_subject_id
                )
            ),
            None
        )


        if not selected_subject:

            messages.error(
                request,
                "You are not assigned to this subject."
            )

            return redirect(
                "mark_attendance"
            )


        # -------------------------------------------------
        # Get students for selected subject
        # -------------------------------------------------

        students = (
            Student.objects
            .filter(
                is_active=True,
                course__subjects=selected_subject,
                semester=selected_subject.semester,
            )
            .select_related(
                "department",
                "course",
                "semester",
                "academic_year",
            )
            .order_by(
                "student_id"
            )
            .distinct()
        )


    # =====================================================
    # SAVE ATTENDANCE
    # =====================================================

    if request.method == "POST":

        subject_id = request.POST.get(
            "subject"
        )

        attendance_date = request.POST.get(
            "date"
        )


        # -------------------------------------------------
        # Verify Faculty Subject Assignment
        # -------------------------------------------------

        assignment_exists = (
            FacultySubjectAssignment.objects
            .filter(
                faculty=faculty,
                subject_id=subject_id,
                is_active=True
            )
            .exists()
        )


        if not assignment_exists:

            messages.error(
                request,
                "You are not assigned to this subject."
            )

            return redirect(
                "mark_attendance"
            )


        subject = get_object_or_404(
            Subject,
            pk=subject_id
        )


        # -------------------------------------------------
        # Get students belonging to this subject
        # -------------------------------------------------

        students = (
            Student.objects
            .filter(
                is_active=True,
                course__subjects=subject,
                semester=subject.semester,
            )
            .distinct()
        )


        # -------------------------------------------------
        # Save / Update attendance
        # -------------------------------------------------

        with transaction.atomic():

            for student in students:

                status = request.POST.get(
                    f"status_{student.id}"
                )


                # Default absent if nothing selected

                if status not in [
                    "PRESENT",
                    "ABSENT"
                ]:

                    status = "ABSENT"


                Attendance.objects.update_or_create(

                    student=student,

                    subject=subject,

                    date=attendance_date,

                    defaults={
                        "faculty": faculty,
                        "status": status,
                    }
                )


        messages.success(
            request,
            "Attendance saved successfully!"
        )


        return redirect(
            f"/attendance/mark/?subject={subject.id}&date={attendance_date}"
        )


    # =====================================================
    # EXISTING ATTENDANCE
    # =====================================================

    existing_attendance = {}


    if selected_subject:

        records = (
            Attendance.objects
            .filter(
                subject=selected_subject,
                date=selected_date,
            )
        )


        existing_attendance = {

            record.student_id:
                record.status

            for record in records

        }


    # =====================================================
    # ATTACH STATUS TO EACH STUDENT
    # =====================================================

    for student in students:

        student.attendance_status = (
            existing_attendance.get(
                student.id,
                ""
            )
        )


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "faculty": faculty,

        "subjects": subjects,

        "students": students,

        "selected_subject":
            selected_subject,

        "selected_subject_id":
            selected_subject_id,

        "selected_date":
            selected_date,

        "existing_attendance":
            existing_attendance,

    }


    return render(
        request,
        "attendance/mark_attendance.html",
        context
    )


# =========================================================
# FACULTY - ATTENDANCE HISTORY
# =========================================================

@login_required
def attendance_history(request):

    try:

        faculty = request.user.faculty_profile

    except Faculty.DoesNotExist:

        messages.error(
            request,
            "Only Faculty can access attendance history."
        )

        return redirect("dashboard")


    # -----------------------------------------------------
    # Only this Faculty's attendance
    # -----------------------------------------------------

    records = (
        Attendance.objects
        .filter(
            faculty=faculty
        )
        .select_related(
            "student",
            "subject",
        )
        .order_by(
            "-date",
            "subject__name",
            "student__student_id",
        )
    )


    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------

    subject_id = request.GET.get(
        "subject"
    )


    selected_date = request.GET.get(
        "date"
    )


    if subject_id:

        records = records.filter(
            subject_id=subject_id
        )


    if selected_date:

        records = records.filter(
            date=selected_date
        )


    # -----------------------------------------------------
    # Faculty assigned subjects
    # -----------------------------------------------------

    subjects = (
        Subject.objects
        .filter(
            faculty_assignments__faculty=faculty,
            faculty_assignments__is_active=True
        )
        .distinct()
    )


    context = {

        "faculty": faculty,

        "records": records,

        "subjects": subjects,

        "selected_subject":
            subject_id,

        "selected_date":
            selected_date,

    }


    return render(
        request,
        "attendance/attendance_history.html",
        context
    )


# =========================================================
# STUDENT - MY ATTENDANCE
# =========================================================

@login_required
def student_attendance(request):

    # -----------------------------------------------------
    # Get logged-in Student
    # -----------------------------------------------------

    try:

        student = request.user.student_profile

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect("dashboard")


    # -----------------------------------------------------
    # IMPORTANT:
    # Only this student's records
    # -----------------------------------------------------

    records = (
        Attendance.objects
        .filter(
            student=student
        )
        .select_related(
            "subject",
            "faculty",
        )
        .order_by(
            "-date"
        )
    )


    # =====================================================
    # OVERALL ATTENDANCE
    # =====================================================

    total = records.count()


    present = records.filter(
        status="PRESENT"
    ).count()


    absent = records.filter(
        status="ABSENT"
    ).count()


    percentage = (

        round(
            (present / total) * 100,
            2
        )

        if total

        else 0

    )


    # =====================================================
    # SUBJECT-WISE ATTENDANCE
    # =====================================================

    subject_ids = (
        records
        .values_list(
            "subject_id",
            flat=True
        )
        .distinct()
    )


    subject_reports = []


    for subject_id in subject_ids:

        subject_records = records.filter(
            subject_id=subject_id
        )


        subject = (
            subject_records
            .first()
            .subject
        )


        subject_total = (
            subject_records.count()
        )


        subject_present = (
            subject_records
            .filter(
                status="PRESENT"
            )
            .count()
        )


        subject_absent = (
            subject_records
            .filter(
                status="ABSENT"
            )
            .count()
        )


        subject_percentage = (

            round(
                (
                    subject_present
                    / subject_total
                ) * 100,
                2
            )

            if subject_total

            else 0

        )


        subject_reports.append({

            "subject":
                subject,

            "total":
                subject_total,

            "present":
                subject_present,

            "absent":
                subject_absent,

            "percentage":
                subject_percentage,

        })


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        "student":
            student,

        "records":
            records,

        "total":
            total,

        "present":
            present,

        "absent":
            absent,

        "percentage":
            percentage,

        "subject_reports":
            subject_reports,

    }


    return render(
        request,
        "attendance/student_attendance.html",
        context
    )