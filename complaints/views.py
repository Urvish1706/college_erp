from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Complaint
from .forms import ComplaintForm
from audit_logs.models import log_action
from notifications.models import create_notification


def is_admin_or_staff(user):
    return user.is_superuser or user.is_staff or (hasattr(user, "profile") and user.profile.role in ["ADMIN", "HOD", "ACCOUNTANT"])


@login_required
def complaint_list(request):
    user = request.user
    admin_status = is_admin_or_staff(user)

    if admin_status:
        complaints_qs = Complaint.objects.select_related("user").all()
    else:
        complaints_qs = Complaint.objects.filter(user=user)

    status_filter = request.GET.get("status", "").strip()
    if status_filter:
        complaints_qs = complaints_qs.filter(status=status_filter)

    q = request.GET.get("q", "").strip()
    if q:
        complaints_qs = complaints_qs.filter(Q(subject__icontains=q) | Q(description__icontains=q))

    complaints_qs = complaints_qs.order_by("-created_at")
    paginator = Paginator(complaints_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "is_admin": admin_status,
        "selected_status": status_filter,
        "q": q,
    }
    return render(request, "complaints/complaint_list.html", context)


@login_required
def complaint_detail(request, pk):
    user = request.user
    admin_status = is_admin_or_staff(user)
    complaint = get_object_or_404(Complaint, pk=pk)

    if not admin_status and complaint.user != user:
        raise PermissionDenied("You are not authorized to view this complaint.")

    context = {
        "complaint": complaint,
        "is_admin": admin_status,
    }
    return render(request, "complaints/complaint_detail.html", context)


@login_required
def complaint_create(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()

            ip = request.META.get("REMOTE_ADDR")
            log_action(request.user, "Grievance Filed", "Complaint", complaint.id, f"Grievance '{complaint.subject}' submitted.", ip_address=ip)

            messages.success(request, "Grievance / Complaint submitted successfully.")
            return redirect("complaint_detail", pk=complaint.pk)
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = ComplaintForm()

    return render(request, "complaints/complaint_form.html", {"form": form, "title": "Submit Grievance / Complaint"})


@login_required
def complaint_update_status(request, pk):
    if not is_admin_or_staff(request.user):
        raise PermissionDenied("Only administrative staff can update complaint status.")

    if request.method != "POST":
        messages.error(request, "Invalid request method for status update.")
        return redirect("complaint_list")

    complaint = get_object_or_404(Complaint, pk=pk)
    new_status = request.POST.get("status")
    response = request.POST.get("admin_response", "").strip()

    if new_status in [choice[0] for choice in Complaint.STATUS_CHOICES]:
        complaint.status = new_status
        if response:
            complaint.admin_response = response
        complaint.save()

        ip = request.META.get("REMOTE_ADDR")
        log_action(request.user, "Complaint Status Updated", "Complaint", complaint.id, f"Complaint '{complaint.subject}' set to {new_status}.", ip_address=ip)

        create_notification(complaint.user, f"Grievance Status: {new_status}", f"Your complaint '{complaint.subject}' status has been updated to {new_status}.", notification_type="SYSTEM", related_url=f"/complaints/{complaint.id}/")

        messages.success(request, f"Complaint status updated to {new_status}.")
    else:
        messages.error(request, "Invalid status option selected.")

    return redirect("complaint_detail", pk=complaint.pk)
