from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Profile


def get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_me(request):
    try:
        profile = Profile.objects.select_related('user').get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(
            user=request.user, display_name=request.user.name)

    if request.method == "GET":
        return Response({
            "id": request.user.id,
            "email": request.user.email,
            "user_type": request.user.user_type,
            "display_name": profile.display_name or request.user.name,
            "photo": profile.photo.url if profile.photo else None,
        })

    display_name = request.data.get("display_name")
    photo = request.FILES.get("photo")

    if display_name:
        profile.display_name = display_name.strip()
    if photo:
        profile.photo = photo

    profile.save()
    return Response({"status": "updated"})
