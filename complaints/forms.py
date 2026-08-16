from django import forms
from .models import Complaint
from config.security import validate_secure_file


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["category", "priority", "subject", "description", "attachment"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Brief Subject / Summary"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Provide full details of your grievance..."}),
            "attachment": forms.FileInput(attrs={"class": "form-control"}),
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        if attachment:
            validate_secure_file(attachment)
        return attachment
