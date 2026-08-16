from django.urls import path

from .views import (
    faculty_list,
    faculty_create,
    faculty_update,
    faculty_detail,
    faculty_delete,
    faculty_assign_subject,
    faculty_remove_subject,
    faculty_login,
    faculty_dashboard,
    faculty_logout,
)


urlpatterns = [

    path(
        "faculty/",
        faculty_list,
        name="faculty_list"
    ),

    path(
        "faculty/add/",
        faculty_create,
        name="faculty_create"
    ),

    path(
        "faculty/<int:pk>/",
        faculty_detail,
        name="faculty_detail"
    ),

    path(
        "faculty/<int:pk>/edit/",
        faculty_update,
        name="faculty_update"
    ),

    path(
        "faculty/<int:pk>/delete/",
        faculty_delete,
        name="faculty_delete"
    ),

    path(
        "faculty/assign-subject/",
        faculty_assign_subject,
        name="faculty_assign_subject"
    ),

    path(
        "faculty/remove-subject/<int:assignment_id>/",
        faculty_remove_subject,
        name="faculty_remove_subject"
    ),

    path(
        "faculty/login/",
        faculty_login,
        name="faculty_login"
    ),

    path(
        "faculty/dashboard/",
        faculty_dashboard,
        name="faculty_dashboard"
    ),

    path(
        "faculty/logout/",
        faculty_logout,
        name="faculty_logout"
    ),

]