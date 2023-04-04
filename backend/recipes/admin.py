"""Admin zone config."""

from django.contrib import admin

from .models import (Recipe, Ingredient, RecipeTag,
                     IngredientRecipe, ShoppingCart, Favorite, Tag)
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin zone registration for User model."""

    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'role',
    )
    search_fields = ('first_name', 'last_name', 'role')
    list_filter = ('first_name', 'last_name', 'email',)
    list_editable = ('__all__',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin zone registration for Recipe model."""

    list_display = ('id', 'name', 'author',)
    search_fields = ('first_name', 'last_name',)
    list_filter = ('author', 'name', 'tag',)
    list_editable = ('__all__',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin zone registration for Ingredient model."""

    list_display = ('id', 'name', 'measurement_unit',)
    list_filter = ('name',)
    list_editable = ('__all__',)


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    """Admin zone registration for RecipeTag model."""

    list_display = ('id', 'recipe', 'tag',)
    search_fields = ('recipe',)
    list_editable = ('__all__',)


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Admin zone registration for IngredientRecipe model."""

    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe',)
    list_editable = ('__all__',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin zone registration for ShoppingCart model."""

    list_display = ('id', 'user', 'recipe',)
    list_filter = ('user',)
    search_fields = ('recipe', 'user',)
    list_editable = ('__all__',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin zone registration for Favorite model."""

    list_display = ('id', 'user', 'recipe',)
    list_filter = ('user',)
    search_fields = ('recipe', 'user',)
    list_editable = ('__all__',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin zone registration for Tag model."""

    list_display = ('id', 'name', 'color', 'slug',)
    list_filter = ('name', 'color',)
    search_fields = ('name',)
    list_editable = ('__all__',)
