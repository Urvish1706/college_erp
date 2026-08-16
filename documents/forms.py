from django import forms
from .models import Document
from config.security import validate_secure_file


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "document_type", "file", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Document Name / Title"}),
            "document_type": forms.Select(attrs={"class": "form-select"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional document details or notes..."}),
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            validate_secure_file(file)
        return file
