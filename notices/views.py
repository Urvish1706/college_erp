from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def notice_list(request):
    return render(request, "notices/notice_list.html")
