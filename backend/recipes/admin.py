"""
Admin zone config recipes.
"""

from django.contrib import admin

from . import models


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin zone registration for Recipe model."""

    list_display = ("id", "author", "name", "text", "image", "cooking_time")
    search_fields = ("first_name", "last_name",)
    list_filter = ("author", "name", "tags",)
    list_editable = ("author", "name", "text", "image", "cooking_time")


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin zone registration for Ingredient model."""

    list_display = ("id", "name", "measurement_unit",)
    list_filter = ("name",)
    list_editable = ("name", "measurement_unit",)


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin zone registration for ShoppingCart model."""

    list_display = ("id", "user", "recipe",)
    list_filter = ("user",)
    search_fields = ("recipe", "user",)
    list_editable = ("user", "recipe",)


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin zone registration for Favorite model."""

    list_display = ("id", "user", "recipe",)
    list_filter = ("user",)
    search_fields = ("recipe", "user",)
    list_editable = ("user", "recipe",)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin zone registration for Tag model."""

    list_display = ("id", "name", "color", "slug",)
    list_filter = ("name", "color",)
    search_fields = ("name",)
    list_editable = ("name", "color", "slug",)
