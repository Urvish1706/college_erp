from django.urls import path
from .views import (
    notification_list,
    mark_notification_as_read,
    mark_all_notifications_as_read,
)

urlpatterns = [
    path("", notification_list, name="notification_list"),
    path("<int:pk>/read/", mark_notification_as_read, name="mark_notification_as_read"),
    path("read-all/", mark_all_notifications_as_read, name="mark_all_notifications_as_read"),
]
