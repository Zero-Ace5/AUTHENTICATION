import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, user_type, name=None):
        email = self.normalize_email(email).lower()
        if not name:
            name = f"USER_{str(uuid.uuid4())[:8]}"
        user = self.model(email=email, user_type=user_type, name=name)
        user.set_unusable_password()
        user.save(using=self.db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = "email"

    @property
    def safe_profile(self):
        from personal_info.models import Profile
        profile, _ = Profile.objects.get_or_create(
            user=self,
            defaults={"display_name": self.name}
        )
        return profile
