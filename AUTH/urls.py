from django.urls import path
from .api_views import start_auth, verify_otp, update_profile
from .views import auth_page, dashboard, logout_view

urlpatterns = [
    path("", auth_page),
    path("dashboard/", dashboard),
    path("logout/", logout_view),

    path("api/auth/start/", start_auth),
    path("api/auth/verify/", verify_otp),
    path("api/profile/update/", update_profile),
]
