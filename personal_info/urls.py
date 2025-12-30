from django.urls import path
from . import views
from .api_views import *

app_name = "personal_info"

urlpatterns = [
    # Page
    path("", views.personal_info_page, name="dashboard"),
    path("edit/", views.edit_profile_page, name="edit_profile"),

    # API
    path("api/profile/me/", profile_me),

]
