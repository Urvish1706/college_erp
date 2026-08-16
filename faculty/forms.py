from django import forms

from .models import (
    Faculty,
    FacultySubjectAssignment,
)


class FacultyForm(forms.ModelForm):

    class Meta:
        model = Faculty

        fields = [
            "faculty_id",
            "profile_photo",
            "first_name",
            "last_name",
            "email",
            "phone",
            "qualification",
            "experience_years",
            "department",
            "joining_date",
            "is_active",
        ]

        widgets = {

            "faculty_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Faculty ID",
                }
            ),

            "profile_photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "First Name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Last Name",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email Address",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Phone Number",
                }
            ),

            "qualification": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. M.Tech, Ph.D",
                }
            ),

            "experience_years": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Years of Experience",
                    "min": 0,
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "joining_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class FacultySubjectAssignmentForm(
    forms.ModelForm
):

    class Meta:
        model = FacultySubjectAssignment

        fields = [
            "faculty",
            "subject",
            "is_active",
        ]

        widgets = {

            "faculty": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "subject": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }