from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
)


class UserManager(BaseUserManager):
    def create_user(self, email, user_type, name=None):
        if not email:
            raise ValueError("Email is required.")

        if not user_type:
            raise ValueError("User type is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, user_type=user_type, name=name or "")
        user.set_unusable_password()
        user.save(using=self.db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    user_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.name:
            self.name = f"USER_{self.id}"
            super().save(update_fields=["name"])

    def __str__(self):
        return self.email
