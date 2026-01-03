from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import login
from django.conf import settings
from django.db import IntegrityError

from .models import User
from .utils import generate_otp
from .emails import send_signup_mail, send_login_email


@api_view(["POST"])
def start_auth(request):
    email = request.data.get("email", "").strip().lower()
    user_type = request.data.get("user_type", "").strip().lower()

    if not email or user_type not in {"student", "teacher", "organization"}:
        return Response({"error": "Invalid data."}, status=400)

    # Cache-aside to prevent DB slams
    user_exists = cache.get(f"user_exists:{email}")
    if user_exists is None:
        user_exists = User.objects.filter(email=email).exists()
        cache.set(f"user_exists:{email}", user_exists, timeout=3600)

    otp = generate_otp()
    cache.set(
        f"auth:otp:{email}",
        {"otp": str(otp), "user_type": user_type},
        timeout=300,
    )

    if not settings.LOAD_TESTING:
        try:
            if user_exists:
                send_login_email(email, otp)
            else:
                send_signup_mail(email, otp, user_type)
        except Exception:
            return Response({"error": "Mail server busy"}, status=500)

    request.session["auth_email"] = email
    return Response({"status": "OTP Sent."})


@api_view(["POST"])
def verify_otp(request):
    # 1. Retrieve data from Session and Request
    email = request.session.get("auth_email")
    otp_input = request.data.get("otp")

    # Fast-fail if session expired or user didn't provide OTP
    if not email or not otp_input:
        return Response({"error": "Session expired or missing OTP"}, status=400)

    # 2. Retrieve OTP and context from Memurai (Redis)
    otp_cache_key = f"auth:otp:{email}"
    cached_data = cache.get(otp_cache_key)

    # Validate OTP
    if not cached_data or cached_data["otp"] != str(otp_input):
        return Response({"error": "Invalid or expired OTP"}, status=401)

    # 3. User & Profile Logic (Optimized for High Load)
    try:
        # Check if user exists
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Create new user if they don't exist
        try:
            user = User.objects.create_user(
                email=email,
                user_type=cached_data["user_type"]
            )

            # Create the Profile immediately (Prevents 'get_or_create' hits later)
            from personal_info.models import Profile
            Profile.objects.create(
                user=user,
                display_name=user.name
            )

            # Update existence cache for start_auth view
            cache.set(f"user_exists:{email}", True, timeout=3600)

        except IntegrityError:
            # Handle rare race condition where two requests create the same user
            user = User.objects.get(email=email)

    # 4. Cleanup and Login
    cache.delete(otp_cache_key)      # OTP is one-time use
    request.session.pop("auth_email", None)  # Clean up session

    login(request, user)

    return Response({
        "status": "ok",
        "user_type": user.user_type,
        "name": user.name,
        "needs_profile_completion": "USER_" in user.name
    })
