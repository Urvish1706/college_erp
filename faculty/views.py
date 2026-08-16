from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from academics.models import Subject
from attendance.models import Attendance
from students.models import Student
from .forms import FacultyForm, FacultySubjectAssignmentForm
from .models import Faculty, FacultySubjectAssignment

@login_required
def faculty_dashboard(request):

    faculty = Faculty.objects.filter(
        user=request.user,
        is_active=True
    ).first()

    if not faculty:
        return redirect("dashboard")

    subjects = Subject.objects.filter(
    faculty_assignments__faculty=faculty,
    faculty_assignments__is_active=True,
    is_active=True
).select_related(
    "course",
    "semester"
).distinct().order_by(
    "semester__number",
    "name"
)

    total_students = Student.objects.filter(
        department=faculty.department,
        is_active=True
    ).count()

    attendance_today = Attendance.objects.filter(
        faculty=faculty
    ).order_by("-date")

    total_attendance = attendance_today.count()

    present_today = attendance_today.filter(
        status="PRESENT"
    ).count()

    absent_today = attendance_today.filter(
        status="ABSENT"
    ).count()

    context = {
        "faculty": faculty,
        "subjects": subjects,
        "total_students": total_students,
        "total_subjects": subjects.count(),
        "total_attendance": total_attendance,
        "present_today": present_today,
        "absent_today": absent_today,
    }

    return render(
        request,
        "faculty/faculty_dashboard.html",
        context
    )

# =========================================================
# FACULTY LIST
# =========================================================

@login_required
def faculty_list(request):

    faculty_members = Faculty.objects.select_related(
        "department",
        "user",
    ).all()

    search = request.GET.get(
        "search",
        ""
    ).strip()

    department = request.GET.get(
        "department",
        ""
    )

    status = request.GET.get(
        "status",
        ""
    )


    # SEARCH
    if search:

        faculty_members = faculty_members.filter(

            Q(
                faculty_id__icontains=search
            )

            |

            Q(
                first_name__icontains=search
            )

            |

            Q(
                last_name__icontains=search
            )

            |

            Q(
                email__icontains=search
            )

        )


    # DEPARTMENT FILTER
    if department:

        faculty_members = faculty_members.filter(
            department_id=department
        )


    # STATUS FILTER
    if status == "active":

        faculty_members = faculty_members.filter(
            is_active=True
        )

    elif status == "inactive":

        faculty_members = faculty_members.filter(
            is_active=False
        )


    # PAGINATION
    paginator = Paginator(
        faculty_members,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    from academics.models import Department


    context = {

        "faculty_members": page_obj,

        "departments": Department.objects.filter(
            is_active=True
        ),

        "search": search,

        "selected_department": department,

        "selected_status": status,

    }


    return render(
        request,
        "faculty/faculty_list.html",
        context
    )


# =========================================================
# ADD FACULTY
# =========================================================

@login_required
def faculty_create(request):

    if request.method == "POST":

        form = FacultyForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            faculty = form.save()

            messages.success(
                request,
                f"{faculty.full_name} added successfully!"
            )

            return redirect(
                "faculty_list"
            )

    else:

        form = FacultyForm()


    return render(
        request,
        "faculty/faculty_form.html",
        {
            "form": form,
            "title": "Add Faculty",
            "button_text": "Add Faculty",
        }
    )


# =========================================================
# EDIT FACULTY
# =========================================================

@login_required
def faculty_update(request, pk):

    faculty = get_object_or_404(
        Faculty,
        pk=pk
    )


    if request.method == "POST":

        form = FacultyForm(
            request.POST,
            request.FILES,
            instance=faculty
        )

        if form.is_valid():

            faculty = form.save()

            messages.success(
                request,
                f"{faculty.full_name} updated successfully!"
            )

            return redirect(
                "faculty_list"
            )

    else:

        form = FacultyForm(
            instance=faculty
        )


    return render(
        request,
        "faculty/faculty_form.html",
        {
            "form": form,
            "faculty": faculty,
            "title": "Edit Faculty",
            "button_text": "Update Faculty",
        }
    )


# =========================================================
# FACULTY DETAIL
# =========================================================

@login_required
def faculty_detail(request, pk):

    faculty = get_object_or_404(
        Faculty.objects.select_related(
            "department",
            "user",
        ),
        pk=pk
    )


    assignments = (
        faculty.subject_assignments
        .filter(
            is_active=True
        )
        .select_related(
            "subject"
        )
    )


    return render(
        request,
        "faculty/faculty_detail.html",
        {
            "faculty": faculty,
            "assignments": assignments,
        }
    )


# =========================================================
# DELETE FACULTY
# =========================================================

@login_required
def faculty_delete(request, pk):

    faculty = get_object_or_404(
        Faculty,
        pk=pk
    )


    if request.method == "POST":

        name = faculty.full_name

        faculty.delete()

        messages.success(
            request,
            f"{name} deleted successfully!"
        )

        return redirect(
            "faculty_list"
        )


    return render(
        request,
        "faculty/faculty_confirm_delete.html",
        {
            "faculty": faculty,
        }
    )


# =========================================================
# ASSIGN SUBJECT TO FACULTY
# =========================================================

@login_required
def faculty_assign_subject(request):

    if request.method == "POST":

        form = FacultySubjectAssignmentForm(
            request.POST
        )

        if form.is_valid():

            assignment = form.save()

            messages.success(
                request,
                (
                    f"{assignment.subject.name} "
                    f"assigned to "
                    f"{assignment.faculty.full_name}."
                )
            )

            return redirect(
                "faculty_list"
            )

    else:

        form = FacultySubjectAssignmentForm()


    return render(
        request,
        "faculty/assign_subject.html",
        {
            "form": form,
        }
    )


# =========================================================
# REMOVE SUBJECT ASSIGNMENT
# =========================================================

@login_required
def faculty_remove_subject(
    request,
    assignment_id
):

    assignment = get_object_or_404(
        FacultySubjectAssignment,
        pk=assignment_id
    )


    if request.method == "POST":

        assignment.is_active = False

        assignment.save(
            update_fields=[
                "is_active"
            ]
        )

        messages.success(
            request,
            "Subject assignment removed."
        )


    return redirect(
        "faculty_list"
    )

# =========================================================
# FACULTY LOGIN
# =========================================================

def faculty_login(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "faculty_profile"):
            return redirect("faculty_dashboard")
        return redirect("dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if hasattr(user, "faculty_profile"):
                faculty = user.faculty_profile

                if not faculty.is_active:
                    messages.error(request, "Your faculty account is inactive.")
                    return redirect("faculty_login")

                login(request, user)
                return redirect("faculty_dashboard")

            messages.error(request, "This account is not registered as Faculty.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "faculty/faculty_login.html")


# =========================================================
# FACULTY LOGOUT
# =========================================================

@login_required
def faculty_logout(request):
    logout(request)
    return redirect("faculty_login")