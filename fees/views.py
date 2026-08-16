from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from students.models import Student


@login_required
def student_fees(request):
    student = Student.objects.filter(user=request.user, is_active=True).first()
    if not student:
        messages.error(request, "Student profile not found.")
        return redirect("dashboard")

    return render(request, "fees/student_fees.html", {"student": student})


@login_required
def fee_list(request):
    return render(request, "fees/fee_list.html")
