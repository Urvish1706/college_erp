from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.utils import timezone

TWO_PLACES = Decimal("0.01")


class Fee(models.Model):
    FEE_TYPE_CHOICES = [
        ("TUITION", "Tuition Fee"),
        ("ADMISSION", "Admission Fee"),
        ("EXAM", "Examination Fee"),
        ("LIBRARY", "Library Fee"),
        ("LAB", "Laboratory Fee"),
        ("HOSTEL", "Hostel Fee"),
        ("TRANSPORT", "Transport Fee"),
        ("OTHER", "Other"),
    ]

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="fees"
    )

    academic_year = models.ForeignKey(
        "academics.AcademicYear",
        on_delete=models.PROTECT,
        related_name="fees"
    )

    course = models.ForeignKey(
        "academics.Course",
        on_delete=models.PROTECT,
        related_name="fees"
    )

    semester = models.ForeignKey(
        "academics.Semester",
        on_delete=models.PROTECT,
        related_name="fees"
    )

    fee_type = models.CharField(
        max_length=50,
        choices=FEE_TYPE_CHOICES
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    due_date = models.DateField()

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.full_name} - {self.get_fee_type_display()} (₹{self.total_amount:.2f})"

    def save(self, *args, **kwargs):
        if self.total_amount:
            self.total_amount = Decimal(str(self.total_amount)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    @property
    def total_paid(self):
        paid = self.payments.aggregate(total=models.Sum("amount"))["total"]
        if paid is None:
            return Decimal("0.00")
        if not isinstance(paid, Decimal):
            paid = Decimal(str(paid))
        return paid.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    @property
    def pending_amount(self):
        rem = self.total_amount - self.total_paid
        if rem <= Decimal("0.00"):
            return Decimal("0.00")
        return rem.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    @property
    def computed_status(self):
        today = timezone.now().date()
        paid = self.total_paid
        pending = self.pending_amount

        if pending == Decimal("0.00") and paid >= self.total_amount:
            return "PAID"
        elif paid > Decimal("0.00") and pending > Decimal("0.00"):
            if today > self.due_date:
                return "OVERDUE"
            return "PARTIAL"
        else:
            if today > self.due_date:
                return "OVERDUE"
            return "PENDING"


class FeePayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("CASH", "Cash"),
        ("UPI", "UPI"),
        ("BANK_TRANSFER", "Bank Transfer"),
        ("CARD", "Card"),
        ("ONLINE", "Online"),
        ("OTHER", "Other"),
    ]

    fee = models.ForeignKey(
        Fee,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    payment_date = models.DateField(
        default=timezone.now
    )

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        default="CASH"
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True
    )

    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-payment_date", "-created_at"]

    def __str__(self):
        return f"{self.receipt_number} - ₹{self.amount} ({self.get_payment_method_display()})"

    def save(self, *args, **kwargs):
        if self.amount:
            self.amount = Decimal(str(self.amount)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        if not self.receipt_number:
            year = timezone.now().year
            count = FeePayment.objects.filter(created_at__year=year).count() + 1
            rec_num = f"FEE-{year}-{count:04d}"
            while FeePayment.objects.filter(receipt_number=rec_num).exists():
                count += 1
                rec_num = f"FEE-{year}-{count:04d}"
            self.receipt_number = rec_num
        super().save(*args, **kwargs)
