"""
Admin zone config users.
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
        "password",
    )
    search_fields = ("username", "first_name", "last_name", "email",)
    list_filter = ("username", "first_name", "last_name", "email",)
    list_editable = ("password",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin zone registration for Subscription model."""

    list_display = ("id", "user", "author",)
    search_fields = ("user", "author",)
