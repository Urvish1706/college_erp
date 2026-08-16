from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .models import Notification


@login_required
def notification_list(request):
    notifications_qs = Notification.objects.filter(recipient=request.user)

    filter_status = request.GET.get("status", "").strip()
    if filter_status == "unread":
        notifications_qs = notifications_qs.filter(is_read=False)

    notifications_qs = notifications_qs.order_by("-created_at")

    paginator = Paginator(notifications_qs, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    context = {
        "page_obj": page_obj,
        "selected_status": filter_status,
        "unread_count": unread_count,
    }
    return render(request, "notifications/notification_list.html", context)


@login_required
def mark_notification_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()

    if notification.related_url:
        return redirect(notification.related_url)
    return redirect("notification_list")


@login_required
def mark_all_notifications_as_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect("notification_list")
