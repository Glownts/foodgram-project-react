"""
Admin zone config.
"""

from django.contrib import admin

from .models import Subscription, User


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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin zone registration for Subscription model."""

    list_display = ("id", "user", "author",)
    search_fields = ("author", "user",)
    list_editable = ("__all__",)
