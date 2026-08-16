from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

from .forms import LoginForm, ProfileForm


def redirect_role_dashboard(user):
    if user.is_superuser or (hasattr(user, "profile") and user.profile.is_admin):
        return redirect("dashboard")
    elif hasattr(user, "faculty_profile") or (hasattr(user, "profile") and user.profile.is_faculty):
        return redirect("faculty_dashboard")
    return redirect("dashboard")


def login_view(request):

    if request.user.is_authenticated:
        return redirect_role_dashboard(request.user)

    if request.method == "POST":

        form = LoginForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            messages.success(
                request,
                f"Welcome back, {user.first_name or user.username}!"
            )

            return redirect_role_dashboard(user)

        messages.error(
            request,
            "Invalid username or password."
        )

    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


@login_required
def profile_view(request):

    from accounts.models import Profile

    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.user.is_superuser:
        profile.role = "ADMIN"
    elif hasattr(request.user, "faculty_profile") and profile.role != "FACULTY":
        profile.role = "FACULTY"
    elif hasattr(request.user, "student_profile") and profile.role != "STUDENT":
        profile.role = "STUDENT"
    profile.save()

    student = getattr(request.user, "student_profile", None)
    faculty = getattr(request.user, "faculty_profile", None)

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Profile updated successfully."
            )
            return redirect("profile")
    else:
        form = ProfileForm(
            instance=profile
        )

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "profile": profile,
            "student": student,
            "faculty": faculty,
        }
    )


class CustomPasswordChangeView(PasswordChangeView):

    form_class = PasswordChangeForm

    template_name = "accounts/password_change.html"

    success_url = "/profile/"

    def form_valid(self, form):

        messages.success(
            self.request,
            "Password changed successfully."
        )

        return super().form_valid(form)