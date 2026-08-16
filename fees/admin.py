from django.contrib import admin
from .models import Fee, FeePayment


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "fee_type",
        "academic_year",
        "semester",
        "total_amount",
        "due_date",
        "is_active",
    )

    search_fields = (
        "student__first_name",
        "student__last_name",
        "student__student_id",
        "fee_type",
    )

    list_filter = (
        "fee_type",
        "academic_year",
        "semester",
        "due_date",
        "is_active",
    )


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "fee",
        "amount",
        "payment_date",
        "payment_method",
        "transaction_id",
    )

    search_fields = (
        "receipt_number",
        "transaction_id",
        "fee__student__first_name",
        "fee__student__last_name",
        "fee__student__student_id",
    )

    list_filter = (
        "payment_method",
        "payment_date",
    )
