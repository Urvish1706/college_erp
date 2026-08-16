from django import forms
from .models import Notice
from config.security import validate_secure_file


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = [
            "title",
            "content",
            "notice_type",
            "priority",
            "target_audience",
            "department",
            "course",
            "semester",
            "publish_date",
            "expiry_date",
            "attachment",
            "is_published",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Notice Headline / Title"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Detailed notice contents..."}),
            "notice_type": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "target_audience": forms.Select(attrs={"class": "form-select"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "course": forms.Select(attrs={"class": "form-select"}),
            "semester": forms.Select(attrs={"class": "form-select"}),
            "publish_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "expiry_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "attachment": forms.FileInput(attrs={"class": "form-control"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        if attachment:
            validate_secure_file(attachment)
        return attachment
