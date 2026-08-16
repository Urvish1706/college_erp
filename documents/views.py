from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Document
from .forms import DocumentUploadForm
from audit_logs.models import log_action


def is_admin_or_staff(user):
    return user.is_superuser or user.is_staff or (hasattr(user, "profile") and user.profile.role in ["ADMIN", "HOD", "ACCOUNTANT"])


@login_required
def document_list(request):
    user = request.user
    admin_status = is_admin_or_staff(user)

    if admin_status:
        docs_qs = Document.objects.select_related("owner").all()
    else:
        docs_qs = Document.objects.filter(owner=user)

    doc_type = request.GET.get("type", "").strip()
    if doc_type:
        docs_qs = docs_qs.filter(document_type=doc_type)

    q = request.GET.get("q", "").strip()
    if q:
        docs_qs = docs_qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    docs_qs = docs_qs.order_by("-created_at")
    paginator = Paginator(docs_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "is_admin": admin_status,
        "selected_type": doc_type,
        "q": q,
    }
    return render(request, "documents/document_list.html", context)


@login_required
def document_upload(request):
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.owner = request.user
            doc.save()

            ip = request.META.get("REMOTE_ADDR")
            log_action(request.user, "Document Uploaded", "Document", doc.id, f"Document '{doc.title}' uploaded.", ip_address=ip)

            messages.success(request, "Document uploaded successfully.")
            return redirect("document_list")
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        form = DocumentUploadForm()

    return render(request, "documents/document_form.html", {"form": form, "title": "Upload New Document"})


@login_required
def document_delete(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    admin_status = is_admin_or_staff(request.user)

    if not admin_status and doc.owner != request.user:
        raise PermissionDenied("You are not authorized to delete this document.")

    if request.method != "POST":
        messages.error(request, "Invalid request method for document deletion.")
        return redirect("document_list")

    title = doc.title
    doc_id = doc.id
    doc.delete()

    ip = request.META.get("REMOTE_ADDR")
    log_action(request.user, "Document Deleted", "Document", doc_id, f"Document '{title}' deleted.", ip_address=ip)

    messages.success(request, f"Document '{title}' deleted successfully.")
    return redirect("document_list")
