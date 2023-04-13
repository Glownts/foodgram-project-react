"""
Serializers.
"""

from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F
from django.db.transaction import atomic
from rest_framework import serializers
from recipes import models
from rest_framework.routers import APIRootView

# -----------------------------------------------------------------------------
#                            Users app
# -----------------------------------------------------------------------------

User = get_user_model()


class BaseAPIRootView(APIRootView):
    """Base paths API's app."""


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Cut version of recipe serializer just for subscriptions."""

    class Meta:
        model = models.Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )
        read_only_fields = "__all__",


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = "is_subscribed",

    def get_is_subscribed(self, obj):
        """User subscription check."""

        user = self.context.get("view").request.user

        if user.is_anonymous or (user == obj):
            return False
        return user.subscriptions.filter(author=obj).exists()

    def create(self, validated_data):
        """User creation method."""

        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class SubscribeSerializer(UserSerializer):
    """Allow to check users subscriptions."""

    recipes = BaseRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        read_only_fields = "__all__",

    def get_is_subscribed(*args):
        """
        Overrides parent"s method. In subscription"s list
        this method always should be True.
        """

        return True

    def get_recipes_count(self, obj):
        """Count number of recipes"""

        return obj.recipes.count()

# -----------------------------------------------------------------------------
#                            Recipe app
# -----------------------------------------------------------------------------


class IngredientSerializer(serializers.ModelSerializer):
    """Show ingredients list."""

    class Meta:
        model = models.Ingredient
        fields = "__all__"
        read_only_fields = "__all__",


class TagSerializer(serializers.ModelSerializer):
    """Show tag list."""

    class Meta:
        model = models.Tag
        fields = "__all__"
        read_only_fields = "__all__",


class RecipeSerializer(serializers.ModelSerializer):
    """Serializers for recipes."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = models.Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "is_favorite",
            "is_shopping_cart",
        )

    def get_ingredients(self, recipe):
        """Get ingredients for recipes."""

        ingredients = recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("recipe__amount")
        )
        return ingredients

    def get_is_favorited(self, recipe):
        """Check if recipe in favorites list."""

        user = self.context.get("view").request.user
        if user.is_anonymous:
            return False

        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Check if recipe in shop list."""

        user = self.context.get("view").request.user
        if user.is_anonymous:
            return False

        return user.carts.filter(recipe=recipe).exists()

    def validate(self, data):
        """Validation for recipe creation or modification."""

        tags_ids = self.initial_data.get("tags")
        ingredients = self.initial_data.get("ingredients")

        if not tags_ids or not ingredients:
            raise ValidationError("Missing data!")

        data.update({
            "tags": tags_ids,
            "ingredients": ingredients,
            "author": self.context.get("request").user
        })
        return data

    # def set_ingredients(self, recipe, ingredients):
    #     models.AmountIngredient.objects.bulk_create(
    #         models.AmountIngredient(
    #             recipe=recipe,
    #             ingredients=ingredient.get('ingredients'),
    #             amount=ingredient.get('amount')
    #         ) for ingredient in ingredients)

    def set_ingredients(self, recipe, ingredients):

        objs = []
        for ingredient, amount in ingredients.values():
            objs.append(models.AmountIngredient(
                recipe=recipe,
                ingredients=ingredient,
                amount=amount
            ))
        models.AmountIngredient.objects.bulk_create(objs)

    @atomic
    def create(self, validated_data):
        """
        Create recipe.

        Use decorator "atomic" to protect DB. If transaction
        will rejected by django, all changes will discard. This
        ensures the safety of DB.
        """

        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = models.Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.set_ingredients(recipe, ingredients)
        return recipe

    @atomic
    def update(self, recipe, validated_data):
        """Create update.

        Use decorator "atomic" to protect DB. If transaction
        will rejected by django, all changes will discard. This
        ensures the safety of DB.
        """

        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            self.set_ingredients(recipe, ingredients)

        recipe.save()
        return recipe
