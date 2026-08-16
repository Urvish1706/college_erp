from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from results.models import Exam
from .models import ExamSchedule
from .forms import ExamForm, ExamScheduleForm
from students.models import Student
from faculty.models import Faculty, FacultySubjectAssignment
from academics.models import Department, Course, Semester, AcademicYear, Subject


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
def exam_list(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)

    if role == "STUDENT":
        return redirect("student_exams")
    elif role == "FACULTY":
        return redirect("faculty_exams")

    exams_qs = Exam.objects.all().select_related("academic_year", "semester").annotate(total_schedules=Count("schedules"))

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        exams_qs = exams_qs.filter(name__icontains=q)

    # Filters
    exam_type = request.GET.get("exam_type", "").strip()
    if exam_type:
        exams_qs = exams_qs.filter(exam_type=exam_type)

    academic_year_id = request.GET.get("academic_year", "").strip()
    if academic_year_id.isdigit():
        exams_qs = exams_qs.filter(academic_year_id=int(academic_year_id))

    semester_id = request.GET.get("semester", "").strip()
    if semester_id.isdigit():
        exams_qs = exams_qs.filter(semester_id=int(semester_id))

    is_published_param = request.GET.get("is_published", "").strip()
    if is_published_param == "1":
        exams_qs = exams_qs.filter(is_published=True)
    elif is_published_param == "0":
        exams_qs = exams_qs.filter(is_published=False)

    is_active_param = request.GET.get("is_active", "").strip()
    if is_active_param == "1":
        exams_qs = exams_qs.filter(is_active=True)
    elif is_active_param == "0":
        exams_qs = exams_qs.filter(is_active=False)

    exams_qs = exams_qs.order_by("-start_date", "-created_at")

    today = timezone.now().date()
    total_exams = Exam.objects.count()
    published_exams = Exam.objects.filter(is_published=True).count()
    upcoming_exams = Exam.objects.filter(is_active=True, start_date__gt=today).count()
    completed_exams = Exam.objects.filter(is_active=True, end_date__lt=today).count()
    todays_exams = Exam.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today).count()

    paginator = Paginator(exams_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "is_admin": True,
        "page_obj": page_obj,
        "exam_types": Exam.EXAM_TYPE_CHOICES,
        "academic_years": AcademicYear.objects.filter(is_active=True),
        "semesters": Semester.objects.filter(is_active=True),
        "q": q,
        "selected_type": exam_type,
        "selected_year": academic_year_id,
        "selected_semester": semester_id,
        "selected_published": is_published_param,
        "selected_active": is_active_param,
        "total_exams": total_exams,
        "published_exams": published_exams,
        "upcoming_exams": upcoming_exams,
        "completed_exams": completed_exams,
        "todays_exams": todays_exams,
    }
    return render(request, "examinations/exam_list.html", context)


@login_required
def exam_detail(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    exam = get_object_or_404(Exam.objects.select_related("academic_year", "semester"), pk=pk)

    if role == "STUDENT" and student:
        if not exam.is_published or not exam.is_active:
            raise PermissionDenied("This exam schedule is not available.")
        if exam.semester_id != student.semester_id or exam.academic_year_id != student.academic_year_id:
            raise PermissionDenied("You are not authorized to view this exam.")

    schedules_qs = ExamSchedule.objects.filter(exam=exam).select_related("subject", "course", "semester", "faculty")

    if role == "STUDENT" and student:
        schedules_qs = schedules_qs.filter(course=student.course, semester=student.semester, is_active=True)

    schedules_qs = schedules_qs.order_by("exam_date", "start_time")

    context = {
        "exam": exam,
        "schedules": schedules_qs,
        "role": role,
        "is_admin": is_admin,
    }
    return render(request, "examinations/exam_detail.html", context)


@login_required
def exam_create(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can create new examinations.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            messages.success(request, f"Exam '{exam.name}' created successfully.")
            return redirect("exam_detail", pk=exam.pk)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = ExamForm()

    return render(request, "examinations/exam_form.html", {
        "form": form,
        "title": "Create New Examination",
        "button_text": "Create Exam"
    })


@login_required
def exam_update(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can edit examinations.")
        return redirect("dashboard")

    exam = get_object_or_404(Exam, pk=pk)

    if request.method == "POST":
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f"Exam '{exam.name}' updated successfully.")
            return redirect("exam_detail", pk=exam.pk)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = ExamForm(instance=exam)

    return render(request, "examinations/exam_form.html", {
        "form": form,
        "exam": exam,
        "title": "Edit Examination",
        "button_text": "Update Exam"
    })


@login_required
def exam_delete(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can delete examinations.")
        return redirect("dashboard")

    exam = get_object_or_404(Exam, pk=pk)

    if request.method == "POST":
        name = exam.name
        exam.delete()
        messages.success(request, f"Exam '{name}' deleted successfully.")
        return redirect("exam_list")

    return render(request, "examinations/exam_confirm_delete.html", {"exam": exam})


@login_required
def exam_toggle_publish(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can publish examinations.")
        return redirect("dashboard")

    exam = get_object_or_404(Exam, pk=pk)
    if request.method == "POST":
        exam.is_published = not exam.is_published
        exam.save()
        status_str = "published" if exam.is_published else "unpublished"
        messages.success(request, f"Exam '{exam.name}' has been {status_str} successfully.")
    return redirect("exam_detail", pk=exam.pk)


@login_required
def schedule_create(request, exam_pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can create exam schedules.")
        return redirect("dashboard")

    exam = get_object_or_404(Exam, pk=exam_pk)

    if request.method == "POST":
        form = ExamScheduleForm(request.POST, exam_instance=exam)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.exam = exam
            schedule.save()
            messages.success(request, f"Exam schedule for '{schedule.subject.name}' added successfully.")
            return redirect("exam_detail", pk=exam.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ExamScheduleForm(exam_instance=exam)

    return render(request, "examinations/schedule_form.html", {
        "form": form,
        "exam": exam,
        "title": f"Add Schedule for {exam.name}",
        "button_text": "Add Schedule Entry"
    })


@login_required
def schedule_update(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can edit exam schedules.")
        return redirect("dashboard")

    schedule = get_object_or_404(ExamSchedule.objects.select_related("exam"), pk=pk)

    if request.method == "POST":
        form = ExamScheduleForm(request.POST, instance=schedule, exam_instance=schedule.exam)
        if form.is_valid():
            form.save()
            messages.success(request, f"Schedule for '{schedule.subject.name}' updated successfully.")
            return redirect("exam_detail", pk=schedule.exam.pk)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = ExamScheduleForm(instance=schedule, exam_instance=schedule.exam)

    return render(request, "examinations/schedule_form.html", {
        "form": form,
        "schedule": schedule,
        "exam": schedule.exam,
        "title": f"Edit Schedule for {schedule.subject.name}",
        "button_text": "Update Schedule Entry"
    })


@login_required
def schedule_delete(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can delete exam schedules.")
        return redirect("dashboard")

    schedule = get_object_or_404(ExamSchedule.objects.select_related("exam", "subject"), pk=pk)
    exam_pk = schedule.exam.pk

    if request.method == "POST":
        subj_name = schedule.subject.name
        schedule.delete()
        messages.success(request, f"Schedule entry for '{subj_name}' deleted successfully.")
        return redirect("exam_detail", pk=exam_pk)

    return render(request, "examinations/schedule_confirm_delete.html", {"schedule": schedule})


@login_required
def student_exams(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not student and not is_admin:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard")

    if student:
        schedules_qs = ExamSchedule.objects.filter(
            exam__is_published=True,
            exam__is_active=True,
            is_active=True,
            course=student.course,
            semester=student.semester,
            academic_year=student.academic_year
        ).select_related("exam", "subject", "faculty")
    else:
        schedules_qs = ExamSchedule.objects.filter(
            exam__is_published=True,
            exam__is_active=True,
            is_active=True
        ).select_related("exam", "subject", "faculty")

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        schedules_qs = schedules_qs.filter(
            Q(exam__name__icontains=q) | Q(subject__name__icontains=q) | Q(subject__code__icontains=q)
        )

    now = timezone.now()
    today = now.date()

    upcoming_schedules = []
    today_schedules = []
    completed_schedules = []

    for sch in schedules_qs.order_by("exam_date", "start_time"):
        if sch.exam_date < today:
            completed_schedules.append(sch)
        elif sch.exam_date == today:
            today_schedules.append(sch)
        else:
            upcoming_schedules.append(sch)

    tab = request.GET.get("tab", "upcoming").lower()

    if tab == "today":
        display_schedules = today_schedules
    elif tab == "completed":
        display_schedules = completed_schedules
    else:
        display_schedules = upcoming_schedules
        tab = "upcoming"

    paginator = Paginator(display_schedules, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "student": student,
        "page_obj": page_obj,
        "q": q,
        "tab": tab,
        "upcoming_count": len(upcoming_schedules),
        "today_count": len(today_schedules),
        "completed_count": len(completed_schedules),
    }
    return render(request, "examinations/student_exams.html", context)


@login_required
def faculty_exams(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not faculty and not is_admin:
        messages.error(request, "Faculty profile not found.")
        return redirect("dashboard")

    if faculty and not is_admin:
        assigned_subject_ids = FacultySubjectAssignment.objects.filter(
            faculty=faculty, is_active=True
        ).values_list("subject_id", flat=True)

        schedules_qs = ExamSchedule.objects.filter(
            Q(subject_id__in=assigned_subject_ids) | Q(faculty=faculty),
            is_active=True,
            exam__is_active=True
        ).select_related("exam", "subject", "course", "semester", "faculty")
    else:
        schedules_qs = ExamSchedule.objects.filter(is_active=True).select_related("exam", "subject", "course", "semester", "faculty")

    q = request.GET.get("q", "").strip()
    if q:
        schedules_qs = schedules_qs.filter(
            Q(exam__name__icontains=q) | Q(subject__name__icontains=q) | Q(room__icontains=q)
        )

    tab = request.GET.get("tab", "all").lower()
    now = timezone.now()
    today = now.date()

    if tab == "invigilation" and faculty:
        schedules_qs = schedules_qs.filter(faculty=faculty)
    elif tab == "today":
        schedules_qs = schedules_qs.filter(exam_date=today)
    elif tab == "upcoming":
        schedules_qs = schedules_qs.filter(exam_date__gt=today)

    schedules_qs = schedules_qs.order_by("exam_date", "start_time")

    paginator = Paginator(schedules_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "faculty": faculty,
        "page_obj": page_obj,
        "q": q,
        "tab": tab,
    }
    return render(request, "examinations/faculty_exams.html", context)


@login_required
def schedule_detail(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    schedule = get_object_or_404(ExamSchedule.objects.select_related("exam", "subject", "course", "semester", "academic_year", "faculty"), pk=pk)

    if role == "STUDENT" and student:
        if not schedule.exam.is_published or not schedule.is_active:
            raise PermissionDenied("Schedule detail is not available.")
        if schedule.course_id != student.course_id or schedule.semester_id != student.semester_id:
            raise PermissionDenied("You are not authorized to view this exam schedule.")

    context = {
        "schedule": schedule,
        "role": role,
        "is_admin": is_admin,
    }
    return render(request, "examinations/schedule_detail.html", context)
