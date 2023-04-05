"""
Models of recipes app. Contain models of recipes, ingredients, tags,
wish-lists and favorites.
"""

from django.conf import settings
from django.db import models
from users.models import User
from core.models import ShoppingCartAndFavorite


class Tag(models.Model):
    """
    Tags to recipes.

    Fields: name, color, slug. All fields are required. All fields must
    be unique.

    Fields "name" and "color" have max length set in the settings by constants
    NAME_MAX_LENG and COLOR_MAX_LENG.

    "color" has choices that described above: BLUE, RED, GREEN, YELLOW
    (голубой, красный, зеленый, желтый).

    Used ordering by "name" field.
    """

    BLUE = "#0000FF"
    RED = "#FF0000"
    GREEN = "#008000"
    YELLOW = "#FFFF00"
    PURPLE = "#8775D2"

    COLOR_CHOICES = [
        (BLUE, "Голубой"),
        (RED, "Красный"),
        (GREEN, "Зеленый"),
        (YELLOW, "Желтый"),
        (PURPLE, "Фиолетовый")
    ]

    name = models.CharField(
        "name",
        max_length=settings.NAME_MAX_LENG,
        unique=True,
        null=False
    )
    color = models.CharField(
        "color",
        max_length=settings.COLOR_MAX_LENG,
        choices=COLOR_CHOICES,
        unique=True,
        null=False
    )
    slug = models.SlugField(
        "slug",
        unique=True,
        null=False
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Ingridients to recipes.

    Fields: name, measurement_unit. All fields are required.

    Fields "name" and "measurement_unit" have max length set in the settings
    by constants NAME_MAX_LENG and MEASUREMENT_MAX_LENG.

    Used ordering by "name" field.
    """

    name = models.CharField(
        "name",
        max_length=settings.NAME_MAX_LENG,
        null=False
    )
    measurement_unit = models.CharField(
        "measurement_unit",
        max_length=settings.MEASUREMENT_MAX_LENG,
        null=False
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Recipes model.

    Fields: tags, author, ingredients, name, image, text, cooking_time,
    pub_date. All fields are required.

    "tag" is many-to-many field that use utility model "RecipeTag" to create
    multiple connections.

    "ingredients" is many-to-many field that use utility model
    "IngredientRecipe" to create multiple connections.

    "name" have max length set in the settings by constant NAME_MAX_LENG.

    "image" is used to upload images in /media/recipes/.

    "pub_date" is the time of publication. It set automatically.

    Used ordering by "-pub_date" field.
    """

    tags = models.ManyToManyField(
        "tags",
        Tag,
        on_delete=models.CASCADE,
        through="RecipeTag",
        related_name="recipes",
    )
    author = models.ForeignKey(
        "author",
        User,
        on_delete=models.SET_DEFAULT,
        default="User deleted",
        related_name="recipes",
        null=False,
    )
    ingredients = models.ManyToManyField(
        "ingredients",
        Ingredient,
        on_delete=models.CASCADE,
        through="IngredientRecipe",
        related_name="recipes"
    )
    name = models.CharField(
        "name",
        max_length=settings.NAME_MAX_LENG,
        null=False
    )
    image = models.ImageField(
        "image",
        upload_to="recipes/",
        blank=False,
        null=False
    )
    text = models.TextField(
        "text",
        null=False
    )
    cooking_time = models.PositiveSmallIntegerField("cooking_time")
    pub_date = models.DateTimeField("publication date", auto_now_add=True)

    class Meta:
        ordering = ("-pub_date",)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """
    Model for creating many-to-many connections between tags and recipes.

    Fields: recipe, tag.
    """

    recipe = models.ForeignKey(
        "recipe",
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        "tag in recipe",
        Tag,
        on_delete=models.CASCADE
    )


class IngredientRecipe(models.Model):
    """
    Model for creating many-to-many connections between ingredients and
    recipes.

    Fields: recipe, ingredient, amount.

    "amount" is used to set the amount of ingredients for a particular recipe.
    """

    ingredient = models.ForeignKey(
        "ingredient in recipe",
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        "recipe",
        Recipe,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        "amout of ingredient",
        null=False
    )


class ShoppingCart(ShoppingCartAndFavorite):
    """
    Recipes to buy.

    Uses standart model from core app. Related names for fields "user"
    and "recipe" overrided.

    Fields: user, recipe, added.

    The pair "user" and "recipe" must be unique.

    "added" is the time of adding recipe in this category.
    It set automatically.

    Used ordering by "-added" field.
    """

    user = models.ForeignKey(related_name="shopping_cart")
    recipe = models.ForeignKey(related_name="shopping_cart")


class Favorite(ShoppingCartAndFavorite):
    """
    Favorite recipes.

    Uses standart model from core app. Related names for fields "user"
    and "recipe" overrided.

    Fields: user, recipe, added.

    The pair "user" and "recipe" must be unique.

    "added" is the time of adding recipe in this category.
    It set automatically.

    Used ordering by "-added" field.
    """

    user = models.ForeignKey(related_name="favorite")
    recipe = models.ForeignKey(related_name="favorite")
