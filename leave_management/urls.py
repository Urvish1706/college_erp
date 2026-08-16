from django.urls import path
from .views import leave_list, leave_create, leave_review

urlpatterns = [
    path("", leave_list, name="leave_list"),
    path("apply/", leave_create, name="leave_create"),
    path("<int:pk>/review/", leave_review, name="leave_review"),
]
