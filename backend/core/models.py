from django.db import models
from users.models import User
from recipes.models import Recipe


class ShoppingCartAndFavorite(models.Model):
    user = models.ForeignKey(
        'user',
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        null=False
    )
    recipe = models.ForeignKey(
        'recipe',
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        null=False
    )
    added = models.DateTimeField('time of adding', auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe',)
        ordering = ["-added"]

    def __str__(self):
        return f"{self.user} added {self.recipe}"
