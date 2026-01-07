from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Profile
from .audit import audit_change


def get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_me(request):

    if request.method == "PATCH":
        print("PATCH HIT")

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

    changed = False

    # ---- display_name audit ----
    if display_name is not None:
        new_name = display_name.strip()
        old_name = profile.display_name or request.user.name

        if new_name != old_name:
            audit_change(
                request=request,
                field="display_name",
                old=old_name,
                new=new_name,
            )
            profile.display_name = new_name
            changed = True

    # ---- photo audit ----
    if photo is not None:
        old_photo = profile.photo.name if profile.photo else None
        new_photo = photo.name

        audit_change(
            request=request,
            field="photo",
            old=old_photo,
            new=new_photo,
        )
        profile.photo = photo
        changed = True

    if changed:
        profile.save()

    return Response({"status": "updated"})
