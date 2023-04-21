"""
Admin zone config recipes.
"""

from django.contrib.admin import ModelAdmin, TabularInline, register

from recipes import models


class IngredientInline(TabularInline):
    model = models.RecipeIngredient
    extra = 2
    min_num = 1


@register(models.Ingredient)
class IngredientAdmin(ModelAdmin):
    """Admin zone registration for Ingredient model."""

    list_display = ("name", "measurement_unit",)
    search_fields = ("name",)
    list_filter = ("name",)


@register(models.Tag)
class TagAdmin(ModelAdmin):
    """Admin zone registration for Tag model."""

    list_display = ("name", "color", "slug",)
    search_fields = ("name", "color",)


@register(models.Recipe)
class RecipeAdmin(ModelAdmin):
    """Admin zone registration for Recipe model."""

    list_display = ("name", "author", "pub_date", "display_tags", "favorite",)
    list_filter = ("name", "author", "tags",)
    search_fields = ("name",)
    readonly_fields = ("favorite",)
    fields = ("image",
              ("name", "author"),
              "text",
              ("tags", "cooking_time"),
              "favorite",)
    inlines = (IngredientInline,)

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = "Tags"

    def favorite(self, obj):
        return obj.favorite.count()


@register(models.RecipeIngredient)
class RecipeIngredientAdmin(ModelAdmin):
    """Admin zone registration for RecipeIngredient model."""

    list_display = ("recipe", "ingredient", "amount",)
    search_fields = ("recipe", "ingredient",)


@register(models.Favorite)
class FavoriteAdmin(ModelAdmin):
    """Admin zone registration for Favorite model."""

    list_display = ("recipe", "user",)
    search_fields = ("recipe", "user",)


@register(models.ShoppingCart)
class ShoppingCartAdmin(ModelAdmin):
    """Admin zone registration for ShoppingCart model."""

    list_display = ("recipe", "user")
    search_fields = ("recipe", "user")
