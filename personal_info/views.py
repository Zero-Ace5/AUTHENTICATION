from django.shortcuts import render
# REMOVE login_required for these specific page-serving views


def personal_info_page(request):
    # This just serves the HTML.
    # The JS inside will check the JWT to get the actual data.
    return render(request, "personal_info/dashboard.html")


def edit_profile_page(request):
    return render(request, "personal_info/edit_profile.html")
