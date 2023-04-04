from django.db import models
from users.models import User
from recipes.models import Recipe


class Shopping_cartAndFavorite(models.Model):
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

    class Meta:
        unique_together = ('user', 'recipe',)
