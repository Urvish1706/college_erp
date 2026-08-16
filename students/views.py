from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from academics.models import (
    Department,
    Course,
    Semester,
)

from .forms import StudentForm
from .models import Student


# =========================================================
# HELPER - GET USER ROLE
# =========================================================

def get_user_role(user):

    if user.is_superuser:
        return "ADMIN"

    profile = getattr(user, "profile", None)

    if profile:
        return profile.role

    # If user has a Student profile, treat as STUDENT
    if Student.objects.filter(
        user=user
    ).exists():
        return "STUDENT"

    return None


# =========================================================
# STUDENT LIST
# =========================================================

@login_required
def student_list(request):

    role = get_user_role(request.user)

    # -----------------------------------------------------
    # STUDENT CAN SEE ONLY OWN PROFILE
    # -----------------------------------------------------

    if role == "STUDENT":

        student = Student.objects.filter(
            user=request.user,
            is_active=True
        ).select_related(
            "department",
            "course",
            "semester",
            "academic_year",
        ).first()

        if not student:

            messages.error(
                request,
                "Student profile not found."
            )

            return redirect("dashboard")

        return render(
            request,
            "students/student_list.html",
            {
                "students": [student],
                "student_only": True,
                "search": "",
                "departments": [],
                "courses": [],
                "semesters": [],
            }
        )


    # -----------------------------------------------------
    # ONLY ADMIN / FACULTY CAN VIEW ALL STUDENTS
    # -----------------------------------------------------

    if role not in ["ADMIN", "FACULTY"]:

        messages.error(
            request,
            "You are not authorized to view students."
        )

        return redirect("dashboard")


    students = Student.objects.select_related(
        "department",
        "course",
        "semester",
        "academic_year",
    ).all()


    search = request.GET.get(
        "search",
        ""
    ).strip()


    department = request.GET.get(
        "department",
        ""
    )


    course = request.GET.get(
        "course",
        ""
    )


    semester = request.GET.get(
        "semester",
        ""
    )


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        students = students.filter(

            Q(
                student_id__icontains=search
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


    # -----------------------------------------------------
    # DEPARTMENT FILTER
    # -----------------------------------------------------

    if department:

        students = students.filter(
            department_id=department
        )


    # -----------------------------------------------------
    # COURSE FILTER
    # -----------------------------------------------------

    if course:

        students = students.filter(
            course_id=course
        )


    # -----------------------------------------------------
    # SEMESTER FILTER
    # -----------------------------------------------------

    if semester:

        students = students.filter(
            semester_id=semester
        )


    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    paginator = Paginator(
        students,
        10
    )

    page_number = request.GET.get(
        "page"
    )

    page_obj = paginator.get_page(
        page_number
    )


    context = {

        "students": page_obj,

        "student_only": False,

        "departments": Department.objects.filter(
            is_active=True
        ),

        "courses": Course.objects.filter(
            is_active=True
        ),

        "semesters": Semester.objects.all(),

        "search": search,

        "selected_department": department,

        "selected_course": course,

        "selected_semester": semester,

    }


    return render(
        request,
        "students/student_list.html",
        context
    )


# =========================================================
# ADD STUDENT
# =========================================================

@login_required
def student_create(request):

    role = get_user_role(request.user)

    if role not in ["ADMIN", "FACULTY"]:

        messages.error(
            request,
            "You are not authorized to add students."
        )

        return redirect("dashboard")


    if request.method == "POST":

        form = StudentForm(
            request.POST,
            request.FILES
        )


        if form.is_valid():

            student = form.save()


            messages.success(
                request,
                f"{student.full_name} added successfully!"
            )


            return redirect(
                "student_list"
            )


    else:

        form = StudentForm()


    return render(
        request,
        "students/student_form.html",
        {
            "form": form,
            "title": "Add Student",
            "button_text": "Add Student",
        }
    )


# =========================================================
# UPDATE STUDENT
# =========================================================

@login_required
def student_update(request, pk):

    role = get_user_role(request.user)

    if role not in ["ADMIN", "FACULTY"]:

        messages.error(
            request,
            "You are not authorized to edit students."
        )

        return redirect("dashboard")


    student = get_object_or_404(
        Student,
        pk=pk
    )


    if request.method == "POST":

        form = StudentForm(
            request.POST,
            request.FILES,
            instance=student
        )


        if form.is_valid():

            student = form.save()


            messages.success(
                request,
                f"{student.full_name} updated successfully!"
            )


            return redirect(
                "student_list"
            )


    else:

        form = StudentForm(
            instance=student
        )


    return render(
        request,
        "students/student_form.html",
        {
            "form": form,
            "student": student,
            "title": "Edit Student",
            "button_text": "Update Student",
        }
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@login_required
def student_delete(request, pk):

    role = get_user_role(request.user)

    if role not in ["ADMIN", "FACULTY"]:

        messages.error(
            request,
            "You are not authorized to delete students."
        )

        return redirect("dashboard")


    student = get_object_or_404(
        Student,
        pk=pk
    )


    if request.method == "POST":

        name = student.full_name

        student.delete()


        messages.success(
            request,
            f"{name} deleted successfully!"
        )


        return redirect(
            "student_list"
        )


    return render(
        request,
        "students/student_confirm_delete.html",
        {
            "student": student,
        }
    )


# =========================================================
# STUDENT DETAIL
# =========================================================

@login_required
def student_detail(request, pk):

    role = get_user_role(request.user)


    # -----------------------------------------------------
    # STUDENT CAN VIEW ONLY OWN PROFILE
    # -----------------------------------------------------

    if role == "STUDENT":

        student = get_object_or_404(
            Student.objects.select_related(
                "department",
                "course",
                "semester",
                "academic_year",
            ),
            pk=pk,
            user=request.user,
            is_active=True,
        )


    # -----------------------------------------------------
    # ADMIN / FACULTY CAN VIEW ANY STUDENT
    # -----------------------------------------------------

    elif role in ["ADMIN", "FACULTY"]:

        student = get_object_or_404(
            Student.objects.select_related(
                "department",
                "course",
                "semester",
                "academic_year",
            ),
            pk=pk
        )


    else:

        messages.error(
            request,
            "You are not authorized to view this profile."
        )

        return redirect(
            "dashboard"
        )


    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
        }
    )


# =========================================================
# STUDENT ATTENDANCE REPORT
# =========================================================

@login_required
def attendance_report(request):

    student = Student.objects.filter(
        user=request.user,
        is_active=True
    ).select_related(
        "department",
        "course",
        "semester",
        "academic_year",
    ).first()

    # Student profile નથી તો dashboard પર મોકલો
    if not student:
        messages.error(
            request,
            "Student profile not found."
        )
        return redirect("dashboard")

    # માત્ર આ logged-in student ના attendance records
    records = student.attendance_records.select_related(
        "subject",
        "faculty",
    ).order_by("-date")

    overall = records.aggregate(
        total=Count("id"),
        present=Count(
            "id",
            filter=Q(status="PRESENT")
        )
    )

    total = overall["total"] or 0
    present = overall["present"] or 0
    absent = total - present

    overall_percentage = (
        round((present / total) * 100, 2)
        if total else 0
    )

    subjects = student.course.subjects.filter(
        semester=student.semester,
        is_active=True
    )

    subject_reports = []

    for subject in subjects:

        data = records.filter(
            subject=subject
        ).aggregate(
            total=Count("id"),
            present=Count(
                "id",
                filter=Q(status="PRESENT")
            )
        )

        subject_total = data["total"] or 0
        subject_present = data["present"] or 0
        subject_absent = subject_total - subject_present

        percentage = (
            round(
                (subject_present / subject_total) * 100,
                2
            )
            if subject_total else 0
        )

        subject_reports.append({
            "subject": subject,
            "total": subject_total,
            "present": subject_present,
            "absent": subject_absent,
            "percentage": percentage,
        })

    context = {
        "student": student,
        "records": records,
        "overall_percentage": overall_percentage,
        "total": total,
        "present": present,
        "absent": absent,
        "subject_reports": subject_reports,
    }

    return render(
        request,
        "students/attendance_report.html",
        context
    )