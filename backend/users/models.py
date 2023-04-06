"""
Models of user app. Contain user and follow models.
"""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """
    User model.

    Fields: username, email, first_name, last_name, role, bio.

    Class Roles defines the available options for "role", "role" is
    responsible for the permissions of the particular user.

    "username" is being validated and cannot have the values specified in the
    validation.

    A confirmation code is sent to the specified email.

    "bio" is optional and is filled in by the user separately. This
    is a personal information field.
    """

    class Roles(models.TextChoices):
        USER = "user", "USER"
        ADMIN = "admin", "ADMIN"

    username = models.CharField(
        verbose_name="username",
        validators=(UnicodeUsernameValidator(),),
        max_length=settings.USER_MAX_LENG,
        unique=True,
        help_text=("The set of characters is no more "
                   f"than {settings.NAME_MAX_LENG}."
                   "Only letters, numbers and @/./+/-/_"),
        error_messages={
            "unique": "A user with that name already exists!",
        },
    )
    email = models.EmailField(
        verbose_name="email",
        max_length=settings.EMAIL_MAX_LENG,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="first_name",
        max_length=settings.USER_MAX_LENG,
        null=False,
        blank=False
    )
    last_name = models.CharField(
        verbose_name="last_name",
        max_length=settings.USER_MAX_LENG,
        null=False,
        blank=False
    )
    role = models.CharField(
        verbose_name="role",
        max_length=settings.ROLE_MAX_LENG,
        choices=Roles.choices,
        default=Roles.USER,
        blank=True
    )
    bio = models.TextField(
        verbose_name="biography",
        blank=True,
    )

    REQUIRED_FIELDS = (
        "email",
        "username",
        "first_name",
        "last_name"
    )

    class Meta:
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"],
                name="unique_username_email",
            )
        ]

    @property
    def is_admin(self):
        return self.role == self.Roles.ADMIN

    def __str__(self):
        return f"{self.username} {self.email} {self.role}"


class Subscription(models.Model):
    """
    Subscription to authors.

    Model for creating many-to-many connections between content makers
    and followers.

    Fields: user (follower), author (content maker).

    The pair "user" and "author" must be unique.
    """

    user = models.ForeignKey(
        User,
        verbose_name="subscriber",
        related_name="subscriber",
        on_delete=models.CASCADE,
        null=False
    )
    author = models.ForeignKey(
        User,
        verbose_name="content_maker",
        related_name="content_maker",
        on_delete=models.CASCADE,
        null=False
    )

    class Meta:
        unique_together = ("user", "author",)
