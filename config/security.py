import os
from django.core.exceptions import ValidationError

DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".sh", ".php", ".py", ".js", ".ps1", ".vbs", ".dll", ".so", ".jar"
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB limit


def validate_secure_file(file_obj):
    if not file_obj:
        return file_obj

    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext in DANGEROUS_EXTENSIONS:
        raise ValidationError(f"File upload rejected: Extension '{ext}' is not permitted for security reasons.")

    if hasattr(file_obj, "size") and file_obj.size > MAX_FILE_SIZE_BYTES:
        raise ValidationError(f"File upload rejected: File size ({file_obj.size / (1024*1024):.1f}MB) exceeds the maximum 10MB limit.")

    return file_obj
