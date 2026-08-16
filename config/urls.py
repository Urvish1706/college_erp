from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    return redirect("login")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("", include("accounts.urls")),
    path("", include("dashboard.urls")),
    path("", include("students.urls")),
    path("", include("attendance.urls")),
    path("", include("faculty.urls")),
    path("results/", include("results.urls")),
    path("academics/", include("academics.urls")),
    path("examinations/", include("examinations.urls")),
    path("assignments/", include("assignments.urls")),
    path("fees/", include("fees.urls")),
    path("notices/", include("notices.urls")),
    path("notifications/", include("notifications.urls")),
    path("audit-logs/", include("audit_logs.urls")),
    path("leave/", include("leave_management.urls")),
    path("complaints/", include("complaints.urls")),
    path("documents/", include("documents.urls")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )