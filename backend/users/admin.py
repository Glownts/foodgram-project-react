"""
Admin zone config.
"""

from django.contrib import admin

from .models import User, Follow


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin zone registration for User model."""

    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
    )
    search_fields = ("first_name", "last_name", "role")
    list_filter = ("first_name", "last_name", "email",)
    list_editable = ("__all__",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Admin zone registration for Follow model."""

    list_display = ("id", "user", "author",)
    search_fields = ("author", "user",)
    list_editable = ("__all__",)
