from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Exam, Result

from students.models import Student
from faculty.models import Faculty, FacultySubjectAssignment


@login_required
def result_entry(request):

    faculty = Faculty.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not faculty:
        messages.error(
            request,
            "Faculty profile not found."
        )
        return redirect("dashboard")

    # Facultyના assigned subjects
    assigned_subjects = FacultySubjectAssignment.objects.filter(
        faculty=faculty,
        is_active=True
    ).select_related(
        "subject"
    )

    subjects = [
        assignment.subject
        for assignment in assigned_subjects
    ]

    exams = Exam.objects.all().order_by(
    "-created_at"
)

    selected_exam = None
    selected_subject = None
    students = []

    exam_id = request.GET.get("exam")
    subject_id = request.GET.get("subject")

    # ==========================================
    # SELECT EXAM
    # ==========================================

    if exam_id:

        selected_exam = Exam.objects.filter(
            id=exam_id
        ).first()


    # ==========================================
    # SELECT SUBJECT
    # ==========================================

    if subject_id:

        selected_subject = next(
            (
                subject
                for subject in subjects
                if str(subject.id) == str(subject_id)
            ),
            None
        )


    # ==========================================
    # LOAD STUDENTS
    # ==========================================

    if selected_exam and selected_subject:

        students = Student.objects.filter(
            is_active=True,
            academic_year=selected_exam.academic_year,
            semester=selected_exam.semester,
            course=selected_subject.course
            if hasattr(selected_subject, "course")
            else None
        ).select_related(
            "department",
            "course",
            "semester",
            "academic_year",
        ).order_by(
            "student_id"
        )

        # જો Subject માં course field ન હોય
        if not students.exists():

            students = Student.objects.filter(
                is_active=True,
                academic_year=selected_exam.academic_year,
                semester=selected_exam.semester,
            ).select_related(
                "department",
                "course",
                "semester",
                "academic_year",
            ).order_by(
                "student_id"
            )


        # Existing marks student સાથે attach કરો

        existing_results = Result.objects.filter(
            exam=selected_exam,
            subject=selected_subject,
            faculty=faculty,
        )

        result_map = {
            result.student_id: result
            for result in existing_results
        }

        for student in students:

            student.existing_result = result_map.get(
                student.id
            )


    # ==========================================
    # SAVE RESULTS
    # ==========================================

    if request.method == "POST":

        exam_id = request.POST.get("exam")
        subject_id = request.POST.get("subject")

        selected_exam = get_object_or_404(
            Exam,
            id=exam_id
        )

        selected_subject = next(
            (
                subject
                for subject in subjects
                if str(subject.id) == str(subject_id)
            ),
            None
        )

        if not selected_subject:

            messages.error(
                request,
                "You are not assigned to this subject."
            )

            return redirect(
                "result_entry"
            )


        max_marks = request.POST.get(
            "max_marks",
            "100"
        )


        # ======================================
        # SAVE EACH STUDENT MARK
        # ======================================

        for student in Student.objects.filter(
            is_active=True,
            academic_year=selected_exam.academic_year,
            semester=selected_exam.semester,
        ):

            marks = request.POST.get(
                f"marks_{student.id}"
            )

            remarks = request.POST.get(
                f"remarks_{student.id}",
                ""
            ).strip()


            # Empty marks = skip
            if marks in [None, ""]:

                continue


            try:
                from decimal import Decimal
                marks_value = Decimal(str(marks))
                max_marks_value = Decimal(str(max_marks))

            except (ValueError, TypeError):

                messages.error(
                    request,
                    f"Invalid marks for {student.full_name}."
                )

                continue


            if marks_value < Decimal("0.00"):

                messages.error(
                    request,
                    f"Marks cannot be negative for {student.full_name}."
                )

                continue


            if marks_value > max_marks_value:

                messages.error(
                    request,
                    f"Marks for {student.full_name} cannot be greater than maximum marks."
                )

                continue


            Result.objects.update_or_create(

                exam=selected_exam,

                student=student,

                subject=selected_subject,

                defaults={
                    "faculty": faculty,
                    "marks_obtained": marks_value,
                    "max_marks": max_marks_value,
                    "remarks": remarks,
                }

            )


        messages.success(
            request,
            "Results saved successfully!"
        )

        return redirect(
            f"/results/entry/?exam={selected_exam.id}"
            f"&subject={selected_subject.id}"
        )


    context = {

        "faculty": faculty,

        "subjects": subjects,

        "exams": exams,

        "selected_exam": selected_exam,

        "selected_subject": selected_subject,

        "students": students,

    }

    return render(
        request,
        "results/result_entry.html",
        context
    )

@login_required
def student_results(request):

    student = Student.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not student:
        messages.error(
            request,
            "Student profile not found."
        )
        return redirect("dashboard")

    results = Result.objects.filter(
        student=student,
        exam__is_published=True
    ).select_related(
        "exam",
        "subject",
        "faculty",
    ).order_by(
        "-exam__created_at",
        "subject__name",
    )

    exams = Exam.objects.filter(
        results__student=student,
        is_published=True,
    ).distinct().order_by(
        "-created_at"
    )

    context = {
        "student": student,
        "results": results,
        "exams": exams,
    }

    return render(
        request,
        "results/student_results.html",
        context
    )


@login_required
def exam_list(request):
    """
    Lists exams and allows Admin to publish/unpublish exam results.
    """
    is_admin = request.user.is_superuser or (hasattr(request.user, "profile") and request.user.profile.is_admin)
    is_faculty = hasattr(request.user, "faculty_profile")

    if not (is_admin or is_faculty):
        messages.error(request, "You are not authorized to view exams.")
        return redirect("dashboard")

    exams = Exam.objects.select_related("academic_year", "semester").all().order_by("-created_at")

    return render(
        request,
        "results/exam_list.html",
        {
            "exams": exams,
            "is_admin": is_admin,
        }
    )


@login_required
def toggle_publish(request, exam_id):
    """
    Toggle is_published flag for an exam (Admin only).
    """
    is_admin = request.user.is_superuser or (hasattr(request.user, "profile") and request.user.profile.is_admin)
    if not is_admin:
        messages.error(request, "Only Admin can publish or unpublish exam results.")
        return redirect("exam_list")

    exam = get_object_or_404(Exam, pk=exam_id)
    exam.is_published = not exam.is_published
    exam.save()

    from audit_logs.models import log_action
    from notifications.models import create_notification
    ip = request.META.get("REMOTE_ADDR")
    status = "published" if exam.is_published else "unpublished"

    log_action(request.user, f"Exam Results {status.capitalize()}", "Exam", exam.id, f"Exam '{exam.name}' results set to {status}.", ip_address=ip)

    if exam.is_published:
        enrolled_students = Student.objects.filter(academic_year=exam.academic_year, semester=exam.semester, is_active=True)
        for s in enrolled_students:
            if s.user:
                create_notification(s.user, f"Results Published: {exam.name}", f"Official results for {exam.name} have been published.", notification_type="RESULT", related_url="/results/my-results/")

    messages.success(request, f"Exam '{exam.name}' has been {status} successfully.")

    return redirect("exam_list")