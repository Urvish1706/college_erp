from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Assignment, AssignmentSubmission
from .forms import AssignmentForm, StudentSubmissionForm, GradeSubmissionForm
from students.models import Student
from faculty.models import Faculty, FacultySubjectAssignment
from academics.models import Subject, Course, Semester, AcademicYear


def get_user_role_and_profiles(user):
    is_admin = user.is_superuser or user.is_staff or (hasattr(user, "profile") and user.profile.role == "ADMIN")
    faculty = Faculty.objects.filter(user=user, is_active=True).first()
    student = Student.objects.filter(user=user, is_active=True).first()

    if is_admin:
        role = "ADMIN"
    elif faculty:
        role = "FACULTY"
    elif student:
        role = "STUDENT"
    else:
        role = "STUDENT"

    return role, is_admin, faculty, student


@login_required
def student_assignments(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not student and not is_admin:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard")

    if student:
        assignments_qs = Assignment.objects.filter(
            course=student.course,
            semester=student.semester,
            academic_year=student.academic_year,
            is_active=True
        ).select_related("subject", "faculty", "course", "semester")
    else:
        assignments_qs = Assignment.objects.filter(is_active=True).select_related("subject", "faculty", "course", "semester")

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        assignments_qs = assignments_qs.filter(
            Q(title__icontains=q) | Q(subject__name__icontains=q) | Q(subject__code__icontains=q)
        )

    # Filter status
    status_filter = request.GET.get("status", "").strip()
    now = timezone.now()

    # Pre-fetch student submissions
    submissions_dict = {}
    if student:
        student_submissions = AssignmentSubmission.objects.filter(
            student=student,
            assignment__in=assignments_qs
        )
        submissions_dict = {sub.assignment_id: sub for sub in student_submissions}

    assignment_items = []
    pending_count = 0
    due_soon_count = 0
    submitted_count = 0

    for a in assignments_qs:
        sub = submissions_dict.get(a.id)
        if sub:
            if sub.status == "GRADED":
                display_badge = "Graded"
                badge_class = "bg-success"
            elif sub.status == "LATE":
                display_badge = "Late Submitted"
                badge_class = "bg-warning text-dark"
            else:
                display_badge = "Submitted"
                badge_class = "bg-info text-dark"
            submitted_count += 1
        else:
            if now > a.due_date:
                display_badge = "Overdue"
                badge_class = "bg-danger"
            elif (a.due_date - now).total_seconds() <= 86400 * 2:
                display_badge = "Due Soon"
                badge_class = "bg-warning text-dark"
                due_soon_count += 1
                pending_count += 1
            else:
                display_badge = "Active"
                badge_class = "bg-primary"
                pending_count += 1

        # Apply status filter
        if status_filter:
            if status_filter == "PENDING" and sub:
                continue
            elif status_filter == "SUBMITTED" and (not sub or sub.status == "GRADED"):
                continue
            elif status_filter == "GRADED" and (not sub or sub.status != "GRADED"):
                continue
            elif status_filter == "OVERDUE" and (sub or now <= a.due_date):
                continue

        assignment_items.append({
            "assignment": a,
            "submission": sub,
            "display_badge": display_badge,
            "badge_class": badge_class,
        })

    paginator = Paginator(assignment_items, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "student": student,
        "page_obj": page_obj,
        "q": q,
        "status_filter": status_filter,
        "total_assignments": len(assignment_items),
        "pending_count": pending_count,
        "due_soon_count": due_soon_count,
        "submitted_count": submitted_count,
    }
    return render(request, "assignments/student_assignments.html", context)


@login_required
def faculty_assignments(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not faculty and not is_admin:
        messages.error(request, "Faculty profile not found.")
        return redirect("dashboard")

    if faculty and not is_admin:
        assignments_qs = Assignment.objects.filter(faculty=faculty).select_related("subject", "course", "semester", "academic_year")
    else:
        assignments_qs = Assignment.objects.all().select_related("subject", "faculty", "course", "semester", "academic_year")

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        assignments_qs = assignments_qs.filter(
            Q(title__icontains=q) | Q(subject__name__icontains=q) | Q(course__name__icontains=q)
        )

    subject_id = request.GET.get("subject", "").strip()
    if subject_id.isdigit():
        assignments_qs = assignments_qs.filter(subject_id=int(subject_id))

    semester_id = request.GET.get("semester", "").strip()
    if semester_id.isdigit():
        assignments_qs = assignments_qs.filter(semester_id=int(semester_id))

    assignments_qs = assignments_qs.annotate(
        total_submissions=Count("submissions"),
        graded_submissions=Count("submissions", filter=Q(submissions__status="GRADED"))
    ).order_by("-due_date", "-created_at")

    paginator = Paginator(assignments_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if faculty and not is_admin:
        assigned_subject_ids = FacultySubjectAssignment.objects.filter(faculty=faculty, is_active=True).values_list("subject_id", flat=True)
        subjects = Subject.objects.filter(id__in=assigned_subject_ids, is_active=True)
    else:
        subjects = Subject.objects.filter(is_active=True)

    semesters = Semester.objects.filter(is_active=True)

    context = {
        "faculty": faculty,
        "is_admin": is_admin,
        "page_obj": page_obj,
        "subjects": subjects,
        "semesters": semesters,
        "q": q,
        "selected_subject": subject_id,
        "selected_semester": semester_id,
    }
    return render(request, "assignments/faculty_assignments.html", context)


@login_required
def assignment_list(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)

    if role == "STUDENT":
        return redirect("student_assignments")
    elif role == "FACULTY":
        return redirect("faculty_assignments")

    assignments_qs = Assignment.objects.all().select_related("subject", "faculty", "course", "semester", "academic_year")

    q = request.GET.get("q", "").strip()
    if q:
        assignments_qs = assignments_qs.filter(
            Q(title__icontains=q) | Q(subject__name__icontains=q) | Q(faculty__first_name__icontains=q) | Q(course__name__icontains=q)
        )

    course_id = request.GET.get("course", "").strip()
    if course_id.isdigit():
        assignments_qs = assignments_qs.filter(course_id=int(course_id))

    subject_id = request.GET.get("subject", "").strip()
    if subject_id.isdigit():
        assignments_qs = assignments_qs.filter(subject_id=int(subject_id))

    status_filter = request.GET.get("status", "").strip()
    if status_filter == "1":
        assignments_qs = assignments_qs.filter(is_active=True)
    elif status_filter == "0":
        assignments_qs = assignments_qs.filter(is_active=False)

    assignments_qs = assignments_qs.annotate(
        total_submissions=Count("submissions"),
        graded_submissions=Count("submissions", filter=Q(submissions__status="GRADED"))
    ).order_by("-due_date", "-created_at")

    total_count = Assignment.objects.count()
    active_count = Assignment.objects.filter(is_active=True).count()
    total_submissions = AssignmentSubmission.objects.count()
    pending_submissions = AssignmentSubmission.objects.exclude(status="GRADED").count()
    graded_submissions = AssignmentSubmission.objects.filter(status="GRADED").count()

    paginator = Paginator(assignments_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "is_admin": True,
        "page_obj": page_obj,
        "courses": Course.objects.filter(is_active=True),
        "subjects": Subject.objects.filter(is_active=True),
        "q": q,
        "selected_course": course_id,
        "selected_subject": subject_id,
        "selected_status": status_filter,
        "total_count": total_count,
        "active_count": active_count,
        "total_submissions": total_submissions,
        "pending_submissions": pending_submissions,
        "graded_submissions": graded_submissions,
    }
    return render(request, "assignments/assignment_list.html", context)


@login_required
def assignment_detail(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    assignment = get_object_or_404(Assignment.objects.select_related("subject", "faculty", "course", "semester", "academic_year"), pk=pk)

    submission = None
    if role == "STUDENT" and student:
        if assignment.course_id != student.course_id or assignment.semester_id != student.semester_id:
            raise PermissionDenied("You are not authorized to view this assignment.")
        submission = AssignmentSubmission.objects.filter(assignment=assignment, student=student).first()

    if role == "FACULTY" and faculty and not is_admin:
        if assignment.faculty_id != faculty.id:
            raise PermissionDenied("You do not have permission to manage this assignment.")

    submissions_summary = None
    if role in ["ADMIN", "FACULTY"]:
        submissions_summary = {
            "total": assignment.submissions.count(),
            "graded": assignment.submissions.filter(status="GRADED").count(),
            "pending": assignment.submissions.exclude(status="GRADED").count(),
        }

    context = {
        "assignment": assignment,
        "submission": submission,
        "role": role,
        "is_admin": is_admin,
        "submissions_summary": submissions_summary,
    }
    return render(request, "assignments/assignment_detail.html", context)


@login_required
def assignment_create(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin and not faculty:
        messages.error(request, "Only faculty and administrators can create assignments.")
        return redirect("dashboard")

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES, faculty=faculty, is_admin=is_admin)
        if form.is_valid():
            assignment = form.save(commit=False)
            if not is_admin and faculty:
                assignment.faculty = faculty
                is_assigned = FacultySubjectAssignment.objects.filter(
                    faculty=faculty, subject=assignment.subject, is_active=True
                ).exists()
                if not is_assigned:
                    messages.error(request, "You are not authorized to create assignments for this subject.")
                    return render(request, "assignments/assignment_form.html", {"form": form, "title": "Create New Assignment", "button_text": "Create Assignment"})

            assignment.save()

            from audit_logs.models import log_action
            from notifications.models import create_notification
            from students.models import Student

            ip = request.META.get("REMOTE_ADDR")
            log_action(request.user, "Assignment Created", "Assignment", assignment.id, f"Assignment '{assignment.title}' created for subject {assignment.subject.name}.", ip_address=ip)

            # Notify students
            enrolled_students = Student.objects.filter(course=assignment.course, semester=assignment.semester, is_active=True)
            for s in enrolled_students:
                if s.user:
                    create_notification(s.user, f"New Assignment: {assignment.title}", f"Subject: {assignment.subject.name}. Due: {assignment.due_date.strftime('%d %b %Y %H:%M')}", notification_type="ASSIGNMENT", related_url=f"/assignments/{assignment.id}/")

            messages.success(request, "Assignment created successfully!")
            if is_admin:
                return redirect("assignment_list")
            return redirect("faculty_assignments")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = AssignmentForm(faculty=faculty, is_admin=is_admin)

    return render(request, "assignments/assignment_form.html", {
        "form": form,
        "title": "Create New Assignment",
        "button_text": "Create Assignment"
    })


@login_required
def assignment_update(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    assignment = get_object_or_404(Assignment, pk=pk)

    if not is_admin:
        if not faculty or assignment.faculty_id != faculty.id:
            raise PermissionDenied("You do not have permission to edit this assignment.")

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES, instance=assignment, faculty=faculty, is_admin=is_admin)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully!")
            return redirect("assignment_detail", pk=assignment.pk)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = AssignmentForm(instance=assignment, faculty=faculty, is_admin=is_admin)

    return render(request, "assignments/assignment_form.html", {
        "form": form,
        "assignment": assignment,
        "title": "Edit Assignment",
        "button_text": "Update Assignment"
    })


@login_required
def assignment_delete(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    assignment = get_object_or_404(Assignment, pk=pk)

    if not is_admin:
        if not faculty or assignment.faculty_id != faculty.id:
            raise PermissionDenied("You do not have permission to delete this assignment.")

    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Assignment deleted successfully.")
        if is_admin:
            return redirect("assignment_list")
        return redirect("faculty_assignments")

    return render(request, "assignments/assignment_confirm_delete.html", {"assignment": assignment})


@login_required
def submit_assignment(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not student:
        messages.error(request, "Only students can submit assignments.")
        return redirect("dashboard")

    assignment = get_object_or_404(Assignment, pk=pk, is_active=True)

    if assignment.course_id != student.course_id or assignment.semester_id != student.semester_id:
        raise PermissionDenied("This assignment is not for your current course/semester.")

    now = timezone.now()
    is_overdue = now > assignment.due_date
    submission = AssignmentSubmission.objects.filter(assignment=assignment, student=student).first()

    if request.method == "POST":
        form = StudentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.student = student
            if is_overdue:
                sub.status = "LATE"
            elif not sub.status or sub.status == "PENDING":
                sub.status = "SUBMITTED"
            sub.save()
            messages.success(request, "Assignment submitted successfully!" if not submission else "Submission updated successfully!")
            return redirect("assignment_detail", pk=assignment.pk)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = StudentSubmissionForm(instance=submission)

    context = {
        "assignment": assignment,
        "form": form,
        "submission": submission,
        "is_overdue": is_overdue,
    }
    return render(request, "assignments/submit_assignment.html", context)


@login_required
def my_submission(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)

    if role == "STUDENT":
        if not student:
            raise PermissionDenied("Student profile not found.")
        submission = get_object_or_404(AssignmentSubmission.objects.select_related("assignment", "assignment__subject", "assignment__faculty", "student"), pk=pk, student=student)
    else:
        submission = get_object_or_404(AssignmentSubmission.objects.select_related("assignment", "assignment__subject", "assignment__faculty", "student"), pk=pk)
        if role == "FACULTY" and not is_admin:
            if submission.assignment.faculty_id != faculty.id:
                raise PermissionDenied("You are not authorized to view this submission.")

    context = {
        "submission": submission,
        "assignment": submission.assignment,
        "role": role,
    }
    return render(request, "assignments/my_submission.html", context)


@login_required
def submission_list(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    assignment = get_object_or_404(Assignment.objects.select_related("subject", "faculty", "course", "semester"), pk=pk)

    if not is_admin:
        if not faculty or assignment.faculty_id != faculty.id:
            raise PermissionDenied("You do not have permission to view submissions for this assignment.")

    submissions_qs = AssignmentSubmission.objects.filter(assignment=assignment).select_related("student", "student__department")

    q = request.GET.get("q", "").strip()
    if q:
        submissions_qs = submissions_qs.filter(
            Q(student__first_name__icontains=q) | Q(student__last_name__icontains=q) | Q(student__student_id__icontains=q)
        )

    status_filter = request.GET.get("status", "").strip()
    if status_filter:
        submissions_qs = submissions_qs.filter(status=status_filter)

    submissions_qs = submissions_qs.order_by("-submitted_at")

    paginator = Paginator(submissions_qs, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "assignment": assignment,
        "page_obj": page_obj,
        "q": q,
        "status_filter": status_filter,
        "total_submissions": submissions_qs.count(),
    }
    return render(request, "assignments/submission_list.html", context)


@login_required
def grade_submission(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    submission = get_object_or_404(AssignmentSubmission.objects.select_related("assignment", "student"), pk=pk)

    if not is_admin:
        if not faculty or submission.assignment.faculty_id != faculty.id:
            raise PermissionDenied("You do not have permission to grade this submission.")

    if request.method == "POST":
        form = GradeSubmissionForm(request.POST, instance=submission, max_marks=submission.assignment.max_marks)
        if form.is_valid():
            graded_sub = form.save(commit=False)
            if not graded_sub.status or graded_sub.status != "RETURNED":
                graded_sub.status = "GRADED"
            graded_sub.save()
            messages.success(request, f"Submission for {submission.student.first_name} {submission.student.last_name} graded successfully!")
            return redirect("submission_list", pk=submission.assignment.pk)
        else:
            messages.error(request, "Please correct the grading errors.")
    else:
        form = GradeSubmissionForm(instance=submission, max_marks=submission.assignment.max_marks)

    context = {
        "submission": submission,
        "assignment": submission.assignment,
        "form": form,
    }
    return render(request, "assignments/grade_submission.html", context)
