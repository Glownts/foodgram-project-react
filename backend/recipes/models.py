"""
Models of recipes app. Contain models of recipes, ingredients, tags,
wish-lists and favorites.
"""

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User


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
        verbose_name="name",
        max_length=settings.NAME_MAX_LENG,
        unique=True,
    )
    color = models.CharField(
        verbose_name="color",
        max_length=settings.COLOR_MAX_LENG,
        choices=COLOR_CHOICES,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="slug",
        max_length=settings.SLUG_MAX_LENG,
        unique=True,
        db_index=False,
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
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
        verbose_name="name",
        max_length=settings.NAME_MAX_LENG,
    )
    measurement_unit = models.CharField(
        verbose_name="measurement_unit",
        max_length=settings.MEASUREMENT_MAX_LENG,
    )

    class Meta:
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    """
    Recipes model.

    Fields: tags, author, ingredients, name, image, text, cooking_time,
    pub_date. All fields are required.

    "name" have max length set in the settings by constant NAME_MAX_LENG.

    "image" is used to upload images in /media/recipes/.

    "pub_date" is the time of publication. It set automatically.

    Used ordering by "-pub_date" field.
    """

    name = models.CharField(
        verbose_name="name",
        max_length=settings.NAME_MAX_LENG,
    )
    author = models.ForeignKey(
        User,
        verbose_name="author",
        related_name="recipes",
        on_delete=models.SET_NULL,
        null=True,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="tags",
        related_name="recipes",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="ingredients",
        related_name="recipes",
    )
    image = models.ImageField(
        verbose_name="image",
        upload_to="recipes/",
    )
    text = models.TextField(
        verbose_name="text",
        max_length=settings.TEXT_MAX_LENG,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="cooking_time",
        default=0,
        validators=(
            MinValueValidator(settings.COOKING_TIME_MIN),
            MaxValueValidator(settings.COOKING_TIME_MAX),
        ),
    )
    pub_date = models.DateTimeField(
        verbose_name="publication date",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ("-pub_date",)

    def __str__(self):
        return f"{self.name}. Author: {self.author.username}"


class AmountIngredient(models.Model):
    """
    Model for creating amount of ingredients in recipes.

    Fields: recipe, ingredient, amount.

    "amount" is used to set the amount of ingredients for a particular recipe.
    """

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="ingredients in recipes",
        related_name="recipe",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="recipes",
        related_name="ingredient",
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name="amount",
        default=0,
        validators=(
            MinValueValidator(
                settings.MIN_AMOUNT_INGREDIENTS,
            ),
            MaxValueValidator(
                settings.MAX_AMOUNT_INGREDIENTS,
            ),
        ),
    )

    class Meta:
        verbose_name = "Ingredients in recipe"
        verbose_name_plural = verbose_name
        ordering = ("recipe", )

    def __str__(self):
        return f"{self.amount} {self.ingredients}"


class ShoppingCart(models.Model):
    """
    Recipes to buy.

    Fields: user, recipe, added.

    The pair "user" and "recipe" must be unique.

    "date_added" is the time of adding recipe in this category.
    It set automatically.

    Used ordering by "-date_added" field.
    """

    user = models.ForeignKey(
        User,
        verbose_name="user",
        related_name="users_shopping_cart",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="recipes",
        related_name="recipe_in_shopping_cart",
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name="time of adding",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Recipes in shopping cart"
        verbose_name_plural = verbose_name
        unique_together = ("user", "recipe",)
        ordering = ["-date_added"]

    def __str__(self):
        return f"{self.user} added {self.recipe}"


class Favorite(models.Model):
    """
    Favorite recipes.

    Fields: user, recipe, added.

    The pair "user" and "recipe" must be unique.

    "date_added" is the time of adding recipe in this category.
    It set automatically.

    Used ordering by "-date_added" field.
    """

    user = models.ForeignKey(
        User,
        verbose_name="user",
        related_name="favorites",
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="recipe",
        related_name="recipes_in_favorite",
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name="time of adding",
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = "Recipes in favorite"
        verbose_name_plural = verbose_name
        unique_together = ("user", "recipe",)
        ordering = ["-date_added"]

    def __str__(self):
        return f"{self.user} added {self.recipe}"
