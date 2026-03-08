from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserRole(models.TextChoices):
    ORG_ADMIN = "ORG_ADMIN", "Organization Admin"
    OFFICE_ADMIN = "OFFICE_ADMIN", "Office Admin"
    OFFICE_MANAGER = "OFFICE_MANAGER", "Office Manager"
    SUPERVISOR = "SUPERVISOR", "Supervisor"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ORG_ADMIN)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user: email as identifier, role and organization for access control."""

    name = models.CharField(max_length=255, blank=True)  # Owner/contact name
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    emp_code = models.CharField(max_length=50, blank=True)  # Employee/office admin code
    designation = models.CharField(max_length=255, blank=True)  # e.g. CEO, Director, Manager
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.OFFICE_MANAGER,
    )
    organization = models.ForeignKey(
        "Organization.Organization",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )
    # Office this user is scoped to (Office Admin, Supervisor). Null = org-wide or manager's offices.
    office = models.ForeignKey(
        "Organization.Office",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users_user"
        ordering = ["email"]

    def __str__(self):
        return self.name or self.email
