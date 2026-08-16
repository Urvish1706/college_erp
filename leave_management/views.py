from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import LeaveApplication
from .forms import LeaveApplicationForm
from audit_logs.models import log_action
from notifications.models import create_notification


def is_admin_or_staff(user):
    return user.is_superuser or user.is_staff or (hasattr(user, "profile") and user.profile.role in ["ADMIN", "HOD", "ACCOUNTANT", "EXAM_CELL"])


@login_required
def leave_list(request):
    user = request.user
    admin_status = is_admin_or_staff(user)

    if admin_status:
        leaves_qs = LeaveApplication.objects.select_related("applicant", "reviewed_by").all()
    else:
        leaves_qs = LeaveApplication.objects.filter(applicant=user).select_related("reviewed_by")

    status_filter = request.GET.get("status", "").strip()
    if status_filter:
        leaves_qs = leaves_qs.filter(status=status_filter)

    q = request.GET.get("q", "").strip()
    if q and admin_status:
        leaves_qs = leaves_qs.filter(Q(applicant__username__icontains=q) | Q(reason__icontains=q))

    leaves_qs = leaves_qs.order_by("-created_at")
    paginator = Paginator(leaves_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "is_admin": admin_status,
        "selected_status": status_filter,
        "q": q,
    }
    return render(request, "leave_management/leave_list.html", context)


@login_required
def leave_create(request):
    if request.method == "POST":
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.applicant = request.user
            leave.save()

            ip = request.META.get("REMOTE_ADDR")
            log_action(request.user, "Leave Applied", "LeaveApplication", leave.id, f"Leave application submitted for {leave.start_date} to {leave.end_date}.", ip_address=ip)

            messages.success(request, "Leave application submitted successfully.")
            return redirect("leave_list")
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = LeaveApplicationForm()

    return render(request, "leave_management/leave_form.html", {"form": form, "title": "Apply for Leave"})


@login_required
def leave_review(request, pk):
    if not is_admin_or_staff(request.user):
        raise PermissionDenied("Only authorized staff can review leave applications.")

    if request.method != "POST":
        messages.error(request, "Invalid request method for leave review.")
        return redirect("leave_list")

    leave = get_object_or_404(LeaveApplication, pk=pk)
    action = request.POST.get("action")
    remarks = request.POST.get("review_remarks", "").strip()

    if action in ["APPROVED", "REJECTED"]:
        leave.status = action
        leave.review_remarks = remarks
        leave.reviewed_by = request.user
        leave.save()

        ip = request.META.get("REMOTE_ADDR")
        log_action(request.user, f"Leave {action.capitalize()}", "LeaveApplication", leave.id, f"Leave application for {leave.applicant.username} set to {action}.", ip_address=ip)

        create_notification(leave.applicant, f"Leave Request {action.capitalize()}", f"Your leave request for {leave.start_date} has been {action.lower()}.", notification_type="SYSTEM", related_url="/leave/")

        messages.success(request, f"Leave application status updated to {action}.")
    else:
        messages.error(request, "Invalid leave action specified.")

    return redirect("leave_list")
