'''Models of recipes app. Contain models of recipes, ingredients,
tags, wish-lists, favorites and follows.'''

from django.db import models
from users.models import User
from core.models import Shopping_cartAndFavorite


class Tag(models.Model):
    '''Tags to recipes.'''
    name = models.CharField(
        'name',
        max_length=128,
        unique=True,
        null=False
    )
    color = models.TextField(
        'color',
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
    tag = models.ForeignKey(
        'tag',
        Tag,
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
    ingredients = models.ForeignKey(
        'ingredients',
        Ingredient,
        on_delete=models.SET_NULL,
        related_name='recipes',
        null=False
    )
    ingredients_amount = models.IntegerField(
        'ingredients_amount',
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
    cooking_time = models.FloatField('cooking_time')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    '''Many-to-many field for tags and recipes.'''
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL)


class Shopping_cart(Shopping_cartAndFavorite):
    '''Recipes to buy.'''


class Favorite(Shopping_cartAndFavorite):
    '''Favorite recipes.'''
    user = models.ForeignKey(related_name='favorite')
    recipe = models.ForeignKey(related_name='favorite')


class Follow(models.Model):
    '''Following to authors.'''
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        null=False
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        null=False
    )

    class Meta:
        unique_together = ('user', 'author',)
