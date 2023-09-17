from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom manager for the CustomUser model.

    This manager provides methods for creating different types of users.
    """

    def create_superuser(
        self, email=None, password=None, user_type="superadmin", **other_fields
    ):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True.")
        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True.")

        return self.create_user(email, password, user_type=user_type, **other_fields)

    def create_user(
        self, email=None, password=None, user_type="customer", **other_fields
    ):
        if not email:
            raise ValueError("You must provide an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, user_type=user_type, **other_fields)
        user.set_password(password)
        user.save()
        return user


# user model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    SUPERADMIN = "superadmin"
    STAFF = "staff"
    CUSTOMER = "customer"

    USER_TYPES = (
        (SUPERADMIN, "Super Admin"),
        (STAFF, "Staff"),
        (CUSTOMER, "Customer"),
    )

    email = models.EmailField("email address", unique=True)
    name = models.CharField(max_length=150)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default="customer")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return str(self.email)


# profile
class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="user_profile"
    )
    bio = models.TextField(null=True, blank=True)
    # add more field

    def __str__(self):
        return str(self.user.name)
