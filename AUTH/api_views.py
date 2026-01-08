from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken  # New Import

from .models import User, UserDeviceSession  # Added UserDeviceSession
from .utils import generate_otp
from .emails import send_signup_mail, send_login_email

from rest_framework_simplejwt.tokens import RefreshToken


@api_view(["POST"])
@permission_classes([AllowAny])
def start_auth(request):
    email = request.data.get("email", "").strip().lower()
    user_type = request.data.get("user_type", "").strip().lower()

    if not email or user_type not in {"student", "teacher", "organization"}:
        return Response({"error": "Invalid data."}, status=400)

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

    # We still use the Django session temporarily just to hold the email
    # until verify_otp is called.
    request.session["auth_email"] = email
    return Response({"status": "OTP Sent."})


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def verify_otp(request):
    email = request.data.get("email") or request.session.get("auth_email")
    otp_input = request.data.get("otp")

    if not email or not otp_input:
        return Response({"error": "Session expired or missing OTP"}, status=400)

    otp_cache_key = f"auth:otp:{email}"
    cached_data = cache.get(otp_cache_key)

    if not cached_data or cached_data["otp"] != str(otp_input):
        return Response({"error": "Invalid or expired OTP"}, status=401)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        try:
            user = User.objects.create_user(
                email=email,
                user_type=cached_data["user_type"]
            )
            from personal_info.models import Profile
            Profile.objects.create(user=user, display_name=user.name)
            cache.set(f"user_exists:{email}", True, timeout=3600)
        except IntegrityError:
            user = User.objects.get(email=email)

    # --- JWT & SESSION TRACKING LOGIC ---

    # 1. Generate Tokens
    refresh = RefreshToken.for_user(user)

    # 2. Track Device/IP
    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')

    UserDeviceSession.objects.create(
        user=user,
        jti=refresh['jti'],  # Unique ID for this specific token
        ip_address=ip_address,
        user_agent=user_agent
    )

    # 3. Cleanup
    cache.delete(otp_cache_key)
    request.session.flush()  # Clears the temporary auth_email session

    # 4. Prepare Response
    response = Response({
        "status": "ok",
        "access": str(refresh.access_token),  # React saves this in memory
        "user_type": user.user_type,
        "name": user.name,
        "needs_profile_completion": "USER_" in user.name
    })

    # 5. Set Refresh Token in HttpOnly Cookie
    # This is secure and can't be accessed by JS (XSS protection)
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        secure=True,     # Set to False if only testing on localhost without HTTPS
        samesite='Lax',
        path='/api/token/refresh/',  # Only send cookie to the refresh endpoint
    )

    return response


@api_view(["POST"])
@permission_classes([AllowAny])  # Anyone can attempt to logout
def logout_api(request):
    # 1. Get the refresh token from the cookie
    refresh_token = request.COOKIES.get('refresh_token')

    response = Response({"status": "logged out"})

    if refresh_token:
        try:
            # 2. Blacklist the token so it can't be used again
            token = RefreshToken(refresh_token)
            jti = token['jti']
            token.blacklist()

            # 3. Mark your custom device session as inactive
            UserDeviceSession.objects.filter(jti=jti).update(is_active=False)
        except Exception:
            pass  # Token might already be expired or invalid

    # 4. Delete the HttpOnly cookie from the browser
    response.delete_cookie('refresh_token', path='/api/token/refresh/')
    return response
