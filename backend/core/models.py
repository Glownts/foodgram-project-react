"""
Models of core app. Contain model standart model for ShoppingCart and
Favorite models.
"""

from django.db import models

from recipes.models import Recipe
from users.models import User


class ShoppingCartAndFavorite(models.Model):
    """
    Standart model for ShoppingCart and
    Favorite models.

    Uses for creating many-to-many connections between tags and recipes.

    Fields: user, recipe, added.

    The pair "user" and "recipe" must be unique.

    "added" is the time of adding recipe in this category.
    It set automatically.

    Used ordering by "-added" field.
    """
    user = models.ForeignKey(
        "user",
        User,
        on_delete=models.CASCADE,
        null=False
    )
    recipe = models.ForeignKey(
        "recipe",
        Recipe,
        on_delete=models.CASCADE,
        null=False
    )
    added = models.DateTimeField("time of adding", auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe",)
        ordering = ["-added"]

    def __str__(self):
        return f"{self.user} added {self.recipe}"
