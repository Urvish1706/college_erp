from django.urls import path
from .views import (
    notice_list,
    notice_detail,
    notice_create,
    notice_edit,
    notice_delete,
)

urlpatterns = [
    path("", notice_list, name="notice_list"),
    path("create/", notice_create, name="notice_create"),
    path("<int:pk>/", notice_detail, name="notice_detail"),
    path("<int:pk>/edit/", notice_edit, name="notice_edit"),
    path("<int:pk>/delete/", notice_delete, name="notice_delete"),
]
