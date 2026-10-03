from dataclasses import fields
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.auths.models import User

class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = {
        (None, {"fields": ("email", "first_name", "last_name")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    }

    add_fieldsets = {
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2" "is_staff", "is_active",)
        }),
    }