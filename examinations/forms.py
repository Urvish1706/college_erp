from django import forms
from django.core.exceptions import ValidationError
from results.models import Exam
from .models import ExamSchedule
from academics.models import Subject, Course, Semester, AcademicYear
from faculty.models import Faculty


class ExamForm(forms.ModelForm):
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    is_published = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = Exam
        fields = [
            "name",
            "exam_type",
            "academic_year",
            "semester",
            "start_date",
            "end_date",
            "description",
            "is_published",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Mid Term Exam 2026"}),
            "exam_type": forms.Select(attrs={"class": "form-select"}),
            "academic_year": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter exam guidelines or notes"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date cannot be earlier than start date.")
        return cleaned_data


class ExamScheduleForm(forms.ModelForm):
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    class Meta:
        model = ExamSchedule
        fields = [
            "exam",
            "course",
            "semester",
            "academic_year",
            "subject",
            "exam_date",
            "start_time",
            "end_time",
            "room",
            "faculty",
            "max_marks",
            "instructions",
            "is_active",
        ]
        widgets = {
            "exam": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.Select(attrs={"class": "form-select"}),
            "academic_year": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.Select(attrs={"class": "form-select"}),
            "exam_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "room": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Hall A, Room 101"}),
            "faculty": forms.Select(attrs={"class": "form-select"}),
            "max_marks": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "instructions": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Specific instructions for students during this exam subject"}),
        }

    def __init__(self, *args, exam_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        if exam_instance:
            self.fields["exam"].initial = exam_instance
            self.fields["semester"].initial = exam_instance.semester
            self.fields["academic_year"].initial = exam_instance.academic_year

    def clean_max_marks(self):
        max_marks = self.cleaned_data.get("max_marks")
        if max_marks is not None and float(max_marks) <= 0:
            raise ValidationError("Maximum marks must be greater than zero.")
        return max_marks

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        exam_date = cleaned_data.get("exam_date")
        exam = cleaned_data.get("exam")

        if start_time and end_time and end_time <= start_time:
            raise ValidationError("End time must be later than start time.")

        if exam and exam_date:
            if exam.start_date and exam_date < exam.start_date:
                raise ValidationError(f"Exam date ({exam_date}) cannot be before exam start date ({exam.start_date}).")
            if exam.end_date and exam_date > exam.end_date:
                raise ValidationError(f"Exam date ({exam_date}) cannot be after exam end date ({exam.end_date}).")

        return cleaned_data
