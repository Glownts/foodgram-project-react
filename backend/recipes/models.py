'''Models of recipes app. Contain models of recipes, ingredients,
tags, wish-lists, favorites and follows.'''

from django.db import models
from users.models import User
from core.models import ShoppingCartAndFavorite


class Tag(models.Model):
    '''Tags to recipes.'''

    BLUE = "#0000FF"
    RED = "#FF0000"
    GREEN = "#008000"
    YELLOW = "#FFFF00"

    COLOR_CHOICES = [
        (BLUE, "Голубой"),
        (RED, "Красный"),
        (GREEN, "Зеленый"),
        (YELLOW, "Желтый")
    ]
    name = models.CharField(
        'name',
        max_length=128,
        unique=True,
        null=False
    )
    color = models.CharField(
        'color',
        max_length=7,
        choices=COLOR_CHOICES,
        unique=True,
        null=False
    )
    slug = models.SlugField(
        'slug',
        unique=True,
        null=False
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Ingridients to recipes.'''

    name = models.CharField(
        'name',
        max_length=128,
        null=False
    )
    measurement_unit = models.CharField(
        'measurement_unit',
        max_length=32,
        null=False
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    '''Recipes model.'''

    tags = models.ManyToManyField(
        'tags',
        Tag,
        through='RecipeTag',
        on_delete=models.SET_NULL,
        related_name='recipes',
        null=False
    )
    author = models.ForeignKey(
        'author',
        User,
        on_delete=models.SET_DEFAULT,
        default='User deleted',
        related_name='recipes',
        null=False,
    )
    ingredients = models.ManyToManyField(
        'ingredients',
        Ingredient,
        through='IngredientRecipe',
        on_delete=models.SET_NULL,
        related_name='recipes',
        null=False
    )
    name = models.CharField(
        'name',
        max_length=128,
        null=False
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        null=False
    )
    text = models.TextField(
        'text',
        null=False
    )
    cooking_time = models.PositiveSmallIntegerField('cooking_time')
    pub_date = models.DateTimeField('publication date', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    '''Many-to-many field model for tags and recipes.'''

    recipe = models.ForeignKey(
        'recipe',
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        'tag in recipe',
        Tag,
        on_delete=models.CASCADE
    )


class IngredientRecipe(models.Model):
    '''Many-to-many field model for ingredients and recipes.'''

    ingredient = models.ForeignKey(
        'ingredient in recipe',
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        'amout of ingredient',
        null=False
    )


class ShoppingCart(ShoppingCartAndFavorite):
    '''Recipes to buy.'''


class Favorite(ShoppingCartAndFavorite):
    '''Favorite recipes.'''

    user = models.ForeignKey(related_name='favorite')
    recipe = models.ForeignKey(related_name='favorite')
