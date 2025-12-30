from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    display_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        if self.display_name:
            return self.display_name
        return str(self.user)
