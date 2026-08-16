from django.urls import path
from .views import student_fees, fee_list

urlpatterns = [
    path("my-fees/", student_fees, name="student_fees"),
    path("list/", fee_list, name="fee_list"),
]
