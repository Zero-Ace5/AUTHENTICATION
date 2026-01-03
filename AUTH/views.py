from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.http import require_POST

from django.views.decorators.csrf import ensure_csrf_cookie


# Create your views here.

@ensure_csrf_cookie
def auth_page(request):
    if request.user.is_authenticated:
        return redirect("personal_info:dashboard")
    return render(request, "accounts/auth.html")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("/")
