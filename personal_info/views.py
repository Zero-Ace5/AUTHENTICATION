from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def personal_info_page(request):
    return render(request, "personal_info/dashboard.html")


@login_required
def edit_profile_page(request):
    return render(request, "personal_info/edit_profile.html")
