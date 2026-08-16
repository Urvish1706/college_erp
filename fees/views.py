from decimal import Decimal, ROUND_HALF_UP
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Fee, FeePayment
from .forms import FeeForm, FeePaymentForm
from students.models import Student
from faculty.models import Faculty
from academics.models import Department, Course, Semester, AcademicYear

TWO_PLACES = Decimal("0.01")


def get_user_role_and_profiles(user):
    is_admin = user.is_superuser or user.is_staff or (hasattr(user, "profile") and user.profile.role == "ADMIN")
    faculty = Faculty.objects.filter(user=user, is_active=True).first()
    student = Student.objects.filter(user=user, is_active=True).first()

    if is_admin:
        role = "ADMIN"
    elif faculty:
        role = "FACULTY"
    elif student:
        role = "STUDENT"
    else:
        role = "STUDENT"

    return role, is_admin, faculty, student


@login_required
def fee_list(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)

    if role == "STUDENT":
        return redirect("student_fees")
    elif role == "FACULTY":
        messages.warning(request, "Faculty members do not have access to fee management records.")
        return redirect("dashboard")

    fees_qs = Fee.objects.all().select_related("student", "course", "semester", "academic_year").prefetch_related("payments")

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        fees_qs = fees_qs.filter(
            Q(student__first_name__icontains=q) |
            Q(student__last_name__icontains=q) |
            Q(student__student_id__icontains=q) |
            Q(fee_type__icontains=q) |
            Q(payments__receipt_number__icontains=q) |
            Q(payments__transaction_id__icontains=q)
        ).distinct()

    # Filters
    course_id = request.GET.get("course", "").strip()
    if course_id.isdigit():
        fees_qs = fees_qs.filter(course_id=int(course_id))

    semester_id = request.GET.get("semester", "").strip()
    if semester_id.isdigit():
        fees_qs = fees_qs.filter(semester_id=int(semester_id))

    academic_year_id = request.GET.get("academic_year", "").strip()
    if academic_year_id.isdigit():
        fees_qs = fees_qs.filter(academic_year_id=int(academic_year_id))

    fee_type = request.GET.get("fee_type", "").strip()
    if fee_type:
        fees_qs = fees_qs.filter(fee_type=fee_type)

    status_filter = request.GET.get("status", "").strip()
    if status_filter:
        filtered_ids = [f.id for f in fees_qs if f.computed_status == status_filter]
        fees_qs = fees_qs.filter(id__in=filtered_ids)

    fees_qs = fees_qs.order_by("-created_at")

    # Aggregate Financial Statistics
    all_fees = Fee.objects.filter(is_active=True).prefetch_related("payments")
    today = timezone.now().date()

    total_fees_sum = Decimal("0.00")
    total_collected_sum = Decimal("0.00")
    total_pending_sum = Decimal("0.00")
    total_overdue_sum = Decimal("0.00")
    pending_students_set = set()

    for f in all_fees:
        t_amt = f.total_amount
        p_amt = f.total_paid
        rem = f.pending_amount

        total_fees_sum += t_amt
        total_collected_sum += p_amt
        total_pending_sum += rem

        if f.computed_status == "OVERDUE":
            total_overdue_sum += rem

        if rem > Decimal("0.00"):
            pending_students_set.add(f.student_id)

    raw_todays = FeePayment.objects.filter(payment_date=today).aggregate(total=Sum("amount"))["total"]
    todays_collection = Decimal(str(raw_todays)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP) if raw_todays is not None else Decimal("0.00")

    paginator = Paginator(fees_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "is_admin": True,
        "page_obj": page_obj,
        "courses": Course.objects.filter(is_active=True),
        "semesters": Semester.objects.filter(is_active=True),
        "academic_years": AcademicYear.objects.filter(is_active=True),
        "fee_types": Fee.FEE_TYPE_CHOICES,
        "q": q,
        "selected_course": course_id,
        "selected_semester": semester_id,
        "selected_year": academic_year_id,
        "selected_type": fee_type,
        "selected_status": status_filter,
        "total_fees": total_fees_sum.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "total_collected": total_collected_sum.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "total_pending": total_pending_sum.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "total_overdue": total_overdue_sum.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "todays_collection": todays_collection,
        "pending_students_count": len(pending_students_set),
    }
    return render(request, "fees/fee_list.html", context)


@login_required
def fee_detail(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    fee = get_object_or_404(Fee.objects.select_related("student", "course", "semester", "academic_year"), pk=pk)

    if role == "STUDENT" and student:
        if fee.student_id != student.id:
            raise PermissionDenied("You are not authorized to view this fee record.")

    if role == "FACULTY" and not is_admin:
        raise PermissionDenied("Faculty members cannot view student fee details.")

    payments = fee.payments.all().order_by("-payment_date", "-created_at")

    context = {
        "fee": fee,
        "payments": payments,
        "role": role,
        "is_admin": is_admin,
    }
    return render(request, "fees/fee_detail.html", context)


@login_required
def fee_create(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can create fee records.")
        return redirect("dashboard")

    if request.method == "POST":
        form = FeeForm(request.POST)
        if form.is_valid():
            fee = form.save()
            messages.success(request, f"Fee record created successfully for {fee.student.full_name}.")
            return redirect("fee_detail", pk=fee.pk)
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = FeeForm()

    return render(request, "fees/fee_form.html", {
        "form": form,
        "title": "Create Student Fee Record",
        "button_text": "Create Fee Record"
    })


@login_required
def fee_update(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can edit fee records.")
        return redirect("dashboard")

    fee = get_object_or_404(Fee, pk=pk)

    if request.method == "POST":
        form = FeeForm(request.POST, instance=fee)
        if form.is_valid():
            form.save()
            messages.success(request, f"Fee record updated successfully.")
            return redirect("fee_detail", pk=fee.pk)
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = FeeForm(instance=fee)

    return render(request, "fees/fee_form.html", {
        "form": form,
        "fee": fee,
        "title": f"Edit Fee Record for {fee.student.full_name}",
        "button_text": "Update Fee Record"
    })


@login_required
def fee_delete(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can delete fee records.")
        return redirect("dashboard")

    fee = get_object_or_404(Fee, pk=pk)

    if fee.payments.exists():
        messages.error(request, "Cannot delete fee record with existing payment history. Delete payments first if necessary.")
        return redirect("fee_detail", pk=fee.pk)

    if request.method == "POST":
        stu_name = fee.student.full_name
        fee.delete()
        messages.success(request, f"Fee record for {stu_name} deleted successfully.")
        return redirect("fee_list")

    return render(request, "fees/fee_confirm_delete.html", {"fee": fee})


@login_required
def payment_create(request, fee_pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can record fee payments.")
        return redirect("dashboard")

    fee = get_object_or_404(Fee.objects.select_related("student"), pk=fee_pk)

    if fee.pending_amount <= Decimal("0.00"):
        messages.info(request, "This fee record is already fully paid.")
        return redirect("fee_detail", pk=fee.pk)

    if request.method == "POST":
        form = FeePaymentForm(request.POST, fee_instance=fee)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.fee = fee
            payment.save()

            from audit_logs.models import log_action
            from notifications.models import create_notification
            ip = request.META.get("REMOTE_ADDR")
            log_action(request.user, "Fee Payment Recorded", "FeePayment", payment.id, f"Payment of ₹{payment.amount:.2f} (Receipt: {payment.receipt_number}) recorded for {fee.student.full_name}.", ip_address=ip)
            if fee.student.user:
                create_notification(fee.student.user, "Fee Payment Receipt", f"Payment of ₹{payment.amount:.2f} received. Receipt No: {payment.receipt_number}.", notification_type="FEE", related_url=f"/fees/receipt/{payment.id}/")

            messages.success(request, f"Payment of ₹{payment.amount:.2f} recorded successfully. Receipt No: {payment.receipt_number}")
            return redirect("receipt_view", payment_pk=payment.pk)
        else:
            messages.error(request, "Please correct the payment errors below.")
    else:
        form = FeePaymentForm(fee_instance=fee, initial={"amount": fee.pending_amount, "payment_date": timezone.now().date()})

    return render(request, "fees/payment_form.html", {
        "form": form,
        "fee": fee,
        "title": f"Record Fee Payment for {fee.student.full_name}",
        "button_text": "Record Payment & Generate Receipt"
    })


@login_required
def payment_delete(request, pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    if not is_admin:
        messages.error(request, "Only administrators can delete payment records.")
        return redirect("dashboard")

    payment = get_object_or_404(FeePayment.objects.select_related("fee"), pk=pk)
    fee_pk = payment.fee.pk

    if request.method == "POST":
        rec_num = payment.receipt_number
        payment.delete()
        messages.success(request, f"Payment receipt '{rec_num}' deleted successfully.")
        return redirect("fee_detail", pk=fee_pk)

    return render(request, "fees/payment_confirm_delete.html", {"payment": payment})


@login_required
def payment_history(request, fee_pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    fee = get_object_or_404(Fee.objects.select_related("student", "course", "semester"), pk=fee_pk)

    if role == "STUDENT" and student:
        if fee.student_id != student.id:
            raise PermissionDenied("You are not authorized to view this payment history.")

    payments = fee.payments.all().order_by("-payment_date", "-created_at")

    return render(request, "fees/payment_history.html", {
        "fee": fee,
        "payments": payments,
        "role": role,
        "is_admin": is_admin,
    })


@login_required
def receipt_view(request, payment_pk):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)
    payment = get_object_or_404(FeePayment.objects.select_related("fee__student", "fee__course", "fee__semester", "fee__academic_year"), pk=payment_pk)

    if role == "STUDENT" and student:
        if payment.fee.student_id != student.id:
            raise PermissionDenied("You are not authorized to access this receipt.")

    fee = payment.fee

    context = {
        "payment": payment,
        "fee": fee,
        "student": fee.student,
        "role": role,
        "is_admin": is_admin,
    }
    return render(request, "fees/receipt.html", context)


@login_required
def student_fees(request):
    role, is_admin, faculty, student = get_user_role_and_profiles(request.user)

    if not student and not is_admin:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard")

    if student:
        fees_qs = Fee.objects.filter(student=student, is_active=True).select_related("course", "semester", "academic_year").prefetch_related("payments")
    else:
        fees_qs = Fee.objects.filter(is_active=True).select_related("student", "course", "semester", "academic_year").prefetch_related("payments")

    fees_qs = fees_qs.order_by("-created_at")

    total_fees_sum = Decimal("0.00")
    total_paid_sum = Decimal("0.00")
    total_pending_sum = Decimal("0.00")
    overdue_count = 0

    for f in fees_qs:
        total_fees_sum += f.total_amount
        total_paid_sum += f.total_paid
        total_pending_sum += f.pending_amount

        if f.computed_status == "OVERDUE":
            overdue_count += 1

    paginator = Paginator(fees_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "student": student,
        "page_obj": page_obj,
        "total_fees": total_fees_sum.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "total_paid": total_paid_sum.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "total_pending": total_pending_sum.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
        "overdue_count": overdue_count,
    }
    return render(request, "fees/student_fees.html", context)
