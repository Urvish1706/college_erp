from django.urls import path
from .views import complaint_list, complaint_detail, complaint_create, complaint_update_status

urlpatterns = [
    path("", complaint_list, name="complaint_list"),
    path("create/", complaint_create, name="complaint_create"),
    path("<int:pk>/", complaint_detail, name="complaint_detail"),
    path("<int:pk>/update-status/", complaint_update_status, name="complaint_update_status"),
]
