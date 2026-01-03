from django.urls import path
from .api_views import *
from .views import auth_page, logout_view

urlpatterns = [
    path("", auth_page),

    path("logout/", logout_view),

    path("api/auth/start/", start_auth),
    path("api/auth/verify/", verify_otp),
]
