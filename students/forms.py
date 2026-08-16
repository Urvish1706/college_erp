from django import forms

from .models import Student


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = [
            "student_id",
            "profile_photo",
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_of_birth",
            "gender",
            "address",
            "guardian_name",
            "guardian_phone",
            "department",
            "course",
            "semester",
            "academic_year",
            "is_active",
        ]

        widgets = {

            "student_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter Student ID",
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

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Address",
                }
            ),

            "guardian_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Guardian Name",
                }
            ),

            "guardian_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Guardian Phone",
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "course": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "semester": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "academic_year": forms.Select(
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