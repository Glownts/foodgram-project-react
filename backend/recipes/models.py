"""
Models of recipes app. Contain models of recipes, ingredients, tags,
wish-lists and favorites.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
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
        null=False
    )
    color = models.CharField(
        verbose_name="color",
        max_length=settings.COLOR_MAX_LENG,
        choices=COLOR_CHOICES,
        unique=True,
        null=False
    )
    slug = models.SlugField(
        verbose_name="slug",
        max_length=settings.SLUG_MAX_LENG,
        unique=True,
        null=False
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

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
        null=False
    )
    measurement_unit = models.CharField(
        verbose_name="measurement_unit",
        max_length=settings.MEASUREMENT_MAX_LENG,
        null=False
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"

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
        Tag,
        verbose_name="tags",
        through="RecipeTag",
        related_name="tag_in_recipe",
    )
    author = models.ForeignKey(
        User,
        verbose_name="author",
        on_delete=models.SET_DEFAULT,
        default="User deleted",
        related_name="author_of_recipe",
        null=False,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="ingredients",
        through="IngredientRecipe",
        related_name="ingredients_for_recipe"
    )
    name = models.CharField(
        verbose_name="name",
        max_length=settings.NAME_MAX_LENG,
        null=False
    )
    image = models.ImageField(
        verbose_name="image",
        upload_to="recipes/",
        blank=False,
        null=False
    )
    text = models.TextField(
        verbose_name="text",
        null=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="cooking_time",
        default=1,
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField("publication date", auto_now_add=True)

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    """
    Model for creating many-to-many connections between tags and recipes.

    Fields: recipe, tag.
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="recipe",
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name="tag",
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Tags in recipe"
        verbose_name_plural = verbose_name


class IngredientRecipe(models.Model):
    """
    Model for creating many-to-many connections between ingredients and
    recipes.

    Fields: recipe, ingredient, amount.

    "amount" is used to set the amount of ingredients for a particular recipe.
    """

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name="ingredient",
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="recipe",
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name="amount",
        null=False
    )

    class Meta:
        verbose_name = "Ingredients in recipe"
        verbose_name_plural = verbose_name


class ShoppingCart(models.Model):
    """
    Recipes to buy.

    Fields: user, recipe, added.

    The pair "user" and "recipe" must be unique.

    "added" is the time of adding recipe in this category.
    It set automatically.

    Used ordering by "-added" field.
    """

    user = models.ForeignKey(
        User,
        verbose_name="user",
        related_name="users_shopping_cart",
        on_delete=models.CASCADE,
        null=False
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="recipe",
        related_name="recipe_in_shopping_cart",
        on_delete=models.CASCADE,
        null=False
    )
    added = models.DateTimeField("time of adding", auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe",)
        ordering = ["-added"]
        verbose_name = "Recipes in shopping cart"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user} added {self.recipe}"


class Favorite(models.Model):
    """
    Favorite recipes.

    Fields: user, recipe, added.

    The pair "user" and "recipe" must be unique.

    "added" is the time of adding recipe in this category.
    It set automatically.

    Used ordering by "-added" field.
    """

    user = models.ForeignKey(
        User,
        verbose_name="user",
        related_name="users_favorite",
        on_delete=models.CASCADE,
        null=False
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name="recipe",
        related_name="recipes_in_favorite",
        on_delete=models.CASCADE,
        null=False
    )
    added = models.DateTimeField("time of adding", auto_now_add=True)

    class Meta:
        unique_together = ("user", "recipe",)
        ordering = ["-added"]
        verbose_name = "Recipes in favorite"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user} added {self.recipe}"
