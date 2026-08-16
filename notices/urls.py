from django.urls import path
from .views import notice_list

urlpatterns = [
    path("", notice_list, name="notice_list"),
]
