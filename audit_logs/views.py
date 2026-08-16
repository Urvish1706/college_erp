import csv
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect

from .models import AuditLog


@login_required
def audit_log_list(request):
    is_admin = request.user.is_superuser or request.user.is_staff or (hasattr(request.user, "profile") and request.user.profile.role == "ADMIN")

    if not is_admin:
        raise PermissionDenied("Only administrators can view security audit logs.")

    logs_qs = AuditLog.objects.select_related("user").all()

    # Search & Filter
    q = request.GET.get("q", "").strip()
    if q:
        logs_qs = logs_qs.filter(
            Q(user__username__icontains=q) |
            Q(action__icontains=q) |
            Q(description__icontains=q) |
            Q(model_name__icontains=q) |
            Q(ip_address__icontains=q)
        )

    action_filter = request.GET.get("action", "").strip()
    if action_filter:
        logs_qs = logs_qs.filter(action__icontains=action_filter)

    logs_qs = logs_qs.order_by("-created_at")

    # CSV Export
    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="audit_logs_export.csv"'
        writer = csv.writer(response)
        writer.writerow(["Timestamp", "User", "Action", "Model", "Object ID", "IP Address", "Description"])
        for log in logs_qs[:5000]:
            writer.writerow([
                log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                log.user.username if log.user else "System",
                log.action,
                log.model_name,
                log.object_id,
                log.ip_address or "N/A",
                log.description,
            ])
        return response

    paginator = Paginator(logs_qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "q": q,
        "selected_action": action_filter,
    }
    return render(request, "audit_logs/audit_log_list.html", context)
