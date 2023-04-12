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

    Fields: username, email, first_name, last_name, bio.


    "username" is being validated and cannot have the values specified in the
    validation.

    "bio" is optional and is filled in by the user separately. This
    is a personal information field.
    """

    class Roles(models.TextChoices):
        USER = 'user', 'USER'
        ADMIN = 'admin', 'ADMIN'

    email = models.EmailField(
        verbose_name="email",
        max_length=settings.EMAIL_MAX_LENG,
        unique=True,
    )
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
    first_name = models.CharField(
        verbose_name="first_name",
        max_length=settings.USER_MAX_LENG,
    )
    last_name = models.CharField(
        verbose_name="last_name",
        max_length=settings.USER_MAX_LENG,
    )
    password = models.CharField(
        verbose_name="password",
        max_length=settings.USER_MAX_LENG,
    )
    bio = models.TextField(
        verbose_name="biography",
    )
    role = models.CharField(
        'role',
        max_length=settings.ROLE_MAX_LENG,
        choices=Roles.choices,
        default=Roles.USER,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ("username",)
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"],
                name="unique_username_email",
            )
        ]

    def __str__(self):
        return f"{self.username} {self.email} {self.role}"


class Subscription(models.Model):
    """
    Subscription to authors.

    Model for creating subscriptions to authors.

    Fields: user (subscriber), author, date_added.

    The pair "user" and "author" must be unique.
    """

    user = models.ForeignKey(
        User,
        verbose_name="subscriber",
        related_name="subscriptions",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name="author",
        related_name="subscribers",
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name="date_of_adding",
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        unique_together = ("user", "author",)

    def __str__(self):
        return f"{self.user.username} subscribed to {self.author.username}"
