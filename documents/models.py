from django.db import models
from django.contrib.auth.models import User


class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ("CERTIFICATE", "Academic Certificate"),
        ("MARK_SHEET", "Mark Sheet / Transcript"),
        ("IDENTITY", "Identity Proof (ID/Aadhaar)"),
        ("ADMISSION", "Admission Form / Letter"),
        ("RESEARCH", "Research Paper / Project Report"),
        ("OTHER", "Other Document"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_documents")
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES, default="OTHER")
    file = models.FileField(upload_to="documents/")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.owner.username} - {self.title} ({self.get_document_type_display()})"
