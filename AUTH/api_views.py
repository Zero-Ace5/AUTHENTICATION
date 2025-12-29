from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import login

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

from .models import User
from .utils import generate_otp
from .emails import send_signup_mail, send_login_email


@api_view(["POST"])
def start_auth(request):
    email = request.data.get("email")
    user_type = request.data.get("user_type")

    if not email or not user_type:
        return Response({"error": "Email and User type required."}, status=400)

    email = email.strip().lower()
    user_type = user_type.strip().lower()

    try:
        validate_email(email)
    except ValidationError:
        return Response({"error": "Invalid email address"}, status=400)

    if user_type not in {"student", "teacher", "organization"}:
        return Response({"error": "Invalid user type."}, status=400)

    otp = generate_otp()

    user_exists = User.objects.filter(email=email).exists()

    cache.set(
        f"auth:otp:{email}",
        {
            "otp": str(otp),
            "user_type": user_type,
            "is_new": not user_exists,
        }, timeout=300,
    )

    request.session["auth_email"] = email
    try:
        if user_exists:
            send_login_email(email, otp)
        else:
            send_signup_mail(email, otp, user_type)
    except Exception:
        cache.delete(f"auth:otp:{email}")
        request.session.pop("auth_email", None)
        return Response(
            {"error": "Failed to send email. Please try again."},
            status=500
        )

    return Response({"status": "OTP Sent."})


@api_view(["POST"])
def verify_otp(request):
    email = request.session.get("auth_email")
    otp = request.data.get("otp")

    if not email or not otp or not str(otp).isdigit():
        return Response({"error": "Invalid request"}, status=400)

    data = cache.get(f"auth:otp:{email}")
    if not data or data["otp"] != str(otp):
        return Response({"error": "Invalid or expired otp"}, status=401)

    cache.delete(f"auth:otp:{email}")
    request.session.pop("auth_email", None)

    user, _ = User.objects.get_or_create(
        email=email,
        defaults={"user_type": data["user_type"]},
    )

    login(request, user)

    needs_profile = not user.name or user.name.startswith("USER_")

    return Response({
        "status": "ok",
        "needs_profile_completion": needs_profile,
        "name": user.name,
        "user_type": user.user_type,
    })


@api_view(["POST"])
def update_profile(request):
    if not request.user.is_authenticated:
        return Response({"error": "Not authenticated"}, status=401)

    name = request.data.get("name", "").strip()
    if not name:
        return Response({"error": "Name required"}, status=400)

    request.user.name = name
    request.user.save(update_fields=["name"])

    return Response({"status": "profile_updated"})
