import os
from django import forms
from django.core.exceptions import ValidationError
from .models import Assignment, AssignmentSubmission
from academics.models import Subject, Course, Semester, AcademicYear
from faculty.models import Faculty, FacultySubjectAssignment


ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.ppt', '.pptx',
    '.xls', '.xlsx', '.zip', '.jpg', '.jpeg', '.png'
}

DANGEROUS_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.ps1', '.sh', '.js',
    '.py', '.php', '.html', '.htm', '.svg', '.dll', '.jar'
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


def validate_file_upload(file):
    if not file:
        return
    ext = os.path.splitext(file.name)[1].lower()
    if ext in DANGEROUS_EXTENSIONS or ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File extension '{ext}' is not allowed. "
            f"Allowed types: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX, ZIP, JPG, JPEG, PNG."
        )
    if file.size > MAX_FILE_SIZE_BYTES:
        raise ValidationError("File size cannot exceed 10MB.")


class AssignmentForm(forms.ModelForm):
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        )
    )

    class Meta:
        model = Assignment
        fields = [
            "title",
            "description",
            "course",
            "semester",
            "academic_year",
            "subject",
            "faculty",
            "assigned_date",
            "due_date",
            "max_marks",
            "attachment",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter assignment title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Enter detailed instructions or description"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.Select(attrs={"class": "form-select"}),
            "academic_year": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "faculty": forms.Select(attrs={"class": "form-select"}),
            "assigned_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "due_date": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "max_marks": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "attachment": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, faculty=None, is_admin=False, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_admin and faculty:
            # Faculty can only select subjects assigned to them
            assigned_subject_ids = FacultySubjectAssignment.objects.filter(
                faculty=faculty, is_active=True
            ).values_list("subject_id", flat=True)
            self.fields["subject"].queryset = Subject.objects.filter(id__in=assigned_subject_ids, is_active=True)
            self.fields["faculty"].initial = faculty
            self.fields["faculty"].widget = forms.HiddenInput()

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        if attachment:
            validate_file_upload(attachment)
        return attachment


class StudentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ["submission_text", "submission_file"]
        widgets = {
            "submission_text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Write your submission answer or comments here..."
            }),
            "submission_file": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_submission_file(self):
        file = self.cleaned_data.get("submission_file")
        if file:
            validate_file_upload(file)
        return file

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("submission_file")
        text = cleaned_data.get("submission_text")
        if not file and not (text and text.strip()):
            raise ValidationError("Please upload a submission file or write a text response.")
        return cleaned_data


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ["marks", "feedback", "status"]
        widgets = {
            "marks": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "feedback": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Provide constructive feedback for the student..."
            }),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, max_marks=100, **kwargs):
        from decimal import Decimal
        self.max_marks = Decimal(str(max_marks))
        super().__init__(*args, **kwargs)

    def clean_marks(self):
        from decimal import Decimal
        marks = self.cleaned_data.get("marks")
        if marks is not None:
            if marks < Decimal("0.00"):
                raise ValidationError("Marks cannot be negative.")
            if marks > self.max_marks:
                raise ValidationError(f"Marks cannot exceed maximum assignment marks ({self.max_marks}).")
        return marks
