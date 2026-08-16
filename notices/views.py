from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Notice
from .forms import NoticeForm
from students.models import Student
from faculty.models import Faculty
from audit_logs.models import log_action
from notifications.models import create_notification


def get_user_role(user):
    if user.is_superuser or user.is_staff or (hasattr(user, "profile") and user.profile.role in ["ADMIN", "ACCOUNTANT", "HOD", "EXAM_CELL"]):
        return "ADMIN"
    elif hasattr(user, "faculty_profile") or (hasattr(user, "profile") and user.profile.role == "FACULTY"):
        return "FACULTY"
    return "STUDENT"


@login_required
def notice_list(request):
    user = request.user
    role = get_user_role(user)
    today = timezone.now().date()

    notices_qs = Notice.objects.all()

    if role != "ADMIN":
        # Non-admins only see published, non-expired notices
        notices_qs = notices_qs.filter(is_published=True, publish_date__lte=today).filter(
            Q(expiry_date__isnull=True) | Q(expiry_date__gte=today)
        )

        if role == "FACULTY":
            fac = getattr(user, "faculty_profile", None)
            dept = fac.department if fac else None
            notices_qs = notices_qs.filter(
                Q(target_audience__in=["EVERYONE", "FACULTY"]) |
                Q(target_audience="DEPARTMENT", department=dept)
            )

        elif role == "STUDENT":
            stu = getattr(user, "student_profile", None)
            dept = stu.department if stu else None
            course = stu.course if stu else None
            sem = stu.semester if stu else None

            notices_qs = notices_qs.filter(
                Q(target_audience__in=["EVERYONE", "STUDENTS"]) |
                Q(target_audience="DEPARTMENT", department=dept) |
                Q(target_audience="COURSE", course=course) |
                Q(target_audience="SEMESTER", semester=sem)
            )

    # Search & Filter
    q = request.GET.get("q", "").strip()
    if q:
        notices_qs = notices_qs.filter(Q(title__icontains=q) | Q(content__icontains=q))

    n_type = request.GET.get("type", "").strip()
    if n_type:
        notices_qs = notices_qs.filter(notice_type=n_type)

    priority = request.GET.get("priority", "").strip()
    if priority:
        notices_qs = notices_qs.filter(priority=priority)

    notices_qs = notices_qs.order_by("-priority", "-publish_date", "-created_at")

    paginator = Paginator(notices_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "role": role,
        "q": q,
        "selected_type": n_type,
        "selected_priority": priority,
        "notice_types": Notice.NOTICE_TYPE_CHOICES,
        "priorities": Notice.PRIORITY_CHOICES,
    }
    return render(request, "notices/notice_list.html", context)


@login_required
def notice_detail(request, pk):
    user = request.user
    role = get_user_role(user)
    notice = get_object_or_404(Notice, pk=pk)

    if role != "ADMIN":
        if not notice.is_published or (notice.expiry_date and notice.expiry_date < timezone.now().date()):
            raise PermissionDenied("This notice is no longer accessible.")

    context = {
        "notice": notice,
        "role": role,
    }
    return render(request, "notices/notice_detail.html", context)


@login_required
def notice_create(request):
    role = get_user_role(request.user)
    if role != "ADMIN":
        raise PermissionDenied("Only administrative staff can post institution-wide notices.")

    if request.method == "POST":
        form = NoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()

            ip = request.META.get("REMOTE_ADDR")
            log_action(request.user, "Notice Published", "Notice", notice.id, f"Notice '{notice.title}' published for audience {notice.get_target_audience_display()}.", ip_address=ip)

            # Dispatch notification
            if notice.is_published:
                if notice.target_audience in ["EVERYONE", "STUDENTS"]:
                    students = Student.objects.filter(is_active=True, user__isnull=False)
                    for s in students:
                        create_notification(s.user, f"Notice: {notice.title}", notice.content[:100], notification_type="NOTICE", related_url=f"/notices/{notice.id}/")

            messages.success(request, "Notice published successfully.")
            return redirect("notice_detail", pk=notice.pk)
        else:
            messages.error(request, "Please correct the errors in the notice form below.")
    else:
        form = NoticeForm()

    return render(request, "notices/notice_form.html", {"form": form, "title": "Publish New Notice", "button_text": "Publish Notice"})


@login_required
def notice_edit(request, pk):
    role = get_user_role(request.user)
    if role != "ADMIN":
        raise PermissionDenied("Only administrative staff can edit notices.")

    notice = get_object_or_404(Notice, pk=pk)

    if request.method == "POST":
        form = NoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            notice = form.save()
            ip = request.META.get("REMOTE_ADDR")
            log_action(request.user, "Notice Updated", "Notice", notice.id, f"Notice '{notice.title}' updated.", ip_address=ip)
            messages.success(request, "Notice updated successfully.")
            return redirect("notice_detail", pk=notice.pk)
        else:
            messages.error(request, "Please correct the errors in the notice form below.")
    else:
        form = NoticeForm(instance=notice)

    return render(request, "notices/notice_form.html", {"form": form, "notice": notice, "title": "Edit Notice", "button_text": "Update Notice"})


@login_required
def notice_delete(request, pk):
    role = get_user_role(request.user)
    if role != "ADMIN":
        raise PermissionDenied("Only administrative staff can delete notices.")

    if request.method != "POST":
        messages.error(request, "Invalid request method for notice deletion.")
        return redirect("notice_list")

    notice = get_object_or_404(Notice, pk=pk)
    title = notice.title
    notice_id = notice.id
    notice.delete()

    ip = request.META.get("REMOTE_ADDR")
    log_action(request.user, "Notice Deleted", "Notice", notice_id, f"Notice '{title}' deleted.", ip_address=ip)

    messages.success(request, f"Notice '{title}' deleted successfully.")
    return redirect("notice_list")
