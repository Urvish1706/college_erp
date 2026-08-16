from decimal import Decimal, ROUND_HALF_UP
from django import forms
from django.core.exceptions import ValidationError
from .models import Fee, FeePayment
from students.models import Student
from academics.models import Course, Semester, AcademicYear

TWO_PLACES = Decimal("0.01")


class FeeForm(forms.ModelForm):
    total_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "e.g. 50000.00"})
    )

    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = Fee
        fields = [
            "student",
            "academic_year",
            "course",
            "semester",
            "fee_type",
            "total_amount",
            "due_date",
            "description",
            "is_active",
        ]
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "academic_year": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.Select(attrs={"class": "form-select"}),
            "fee_type": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter fee breakdown or notes"}),
        }

    def clean_total_amount(self):
        amount = self.cleaned_data.get("total_amount")
        if amount is not None:
            if amount <= Decimal("0.00"):
                raise ValidationError("Total fee amount must be greater than zero.")
            amount = amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        return amount


class FeePaymentForm(forms.ModelForm):
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "placeholder": "e.g. 20000.00"})
    )

    class Meta:
        model = FeePayment
        fields = [
            "amount",
            "payment_date",
            "payment_method",
            "transaction_id",
            "reference_number",
            "notes",
        ]
        widgets = {
            "payment_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "transaction_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. UPI/123456789/REF"}),
            "reference_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional bank/receipt reference"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Payment remarks or details"}),
        }

    def __init__(self, *args, fee_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fee_instance = fee_instance

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None:
            if amount <= Decimal("0.00"):
                raise ValidationError("Payment amount must be greater than zero.")

            amount = amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

            if self.fee_instance:
                pending = self.fee_instance.pending_amount
                if self.instance and self.instance.pk:
                    pending += self.instance.amount

                if amount > pending:
                    raise ValidationError(f"Payment amount (₹{amount:.2f}) cannot exceed the remaining pending balance (₹{pending:.2f}).")

        return amount
