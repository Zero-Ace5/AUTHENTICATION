from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_POST

# Create your views here.


def auth_page(request):
    if request.user.is_authenticated:
        return redirect("/dashboard/")
    return render(request, "accounts/auth.html")


@login_required
def dashboard(request):
    user = request.user

    needs_profile = (
        not user.name or user.name.startswith("USER_")
    )

    return render(request, "accounts/dashboard.html", {
        "user": user,
        "needs_profile": needs_profile,
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect("/")
