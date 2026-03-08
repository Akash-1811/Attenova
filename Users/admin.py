from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from Users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "name", "role", "organization", "is_active", "created_at"]
    list_filter = ["role", "is_active"]
    search_fields = ["email", "name"]
    ordering = ["email"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("name", "phone_number", "designation")}),
        ("Access", {"fields": ("role", "organization", "is_active", "is_staff")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
        ("Profile", {"fields": ("name", "phone_number", "designation")}),
        ("Access", {"fields": ("role", "organization", "is_active", "is_staff")}),
    )
