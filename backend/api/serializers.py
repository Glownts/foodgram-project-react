"""
Serializers.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes import models
from users.models import Subscription, User

# -----------------------------------------------------------------------------
#                            Users app
# -----------------------------------------------------------------------------


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Cut version of recipe serializer just for subscriptions."""

    class Meta:
        model = models.Recipe
        fields = ("id", "name", "image", "cooking_time")


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    is_subscribed = serializers.SerializerMethodField(
        method_name="get_is_subscribed"
    )

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

    def get_is_subscribed(self, object):
        """User subscription check."""

        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user,
            author=object.id
        ).exists()

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

    def validate_username(self, value):
        if value in settings.PROHIBITED_NAMES:
            raise ValidationError(settings.USERNAME_ERROR)
        return value


class SubscribeSerializer(UserSerializer):
    """Allow to check users subscriptions."""

    recipes = serializers.SerializerMethodField(
        method_name="get_recipes"
    )
    recipes_count = serializers.SerializerMethodField(
        method_name="get_recipes_count"
    )

    class Meta(UserSerializer.Meta):
        fields = (UserSerializer.Meta.fields
                  + ("recipes", "recipes_count"))

    def get_is_subscribed(*args):
        """
        Overrides parent"s method. In subscription"s list
        this method always should be True.
        """

        return True

    def get_recipes(self, object):
        """Get recipes queryset."""

        request = self.context.get("request")
        context = {"request": request}
        recipe_limit = request.query_params.get("recipe_limit")
        queryset = object.recipes.all()
        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]
        return BaseRecipeSerializer(queryset, context=context, many=True).data

    def get_recipes_count(self, object):
        """Count number of recipes"""

        return object.recipes.count()

# -----------------------------------------------------------------------------
#                            Recipe app
# -----------------------------------------------------------------------------


class IngredientSerializer(serializers.ModelSerializer):
    """Show ingredients list."""

    class Meta:
        model = models.Ingredient
        fields = ("id", "name", "measurement_unit")


class TagSerializer(serializers.ModelSerializer):
    """Show tag list."""

    class Meta:
        model = models.Tag
        fields = "__all__"
        read_only_fields = ("__all__",)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer for detailed description of ingredients in a recipe."""

    name = serializers.CharField(
        source="ingredient.name", read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient.id", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True)

    class Meta:
        model = models.RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class AddIngredientSerializer(serializers.ModelSerializer):
    """Serializer for adding an ingredient when creating a recipe."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all(),
        source="ingredient"
    )

    class Meta:
        model = models.RecipeIngredient
        fields = ("id", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)

    class Meta:
        model = models.Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time"
        )

    def validate(self, data):
        """Validation."""

        cooking_time = data["cooking_time"]
        tags = data["tags"]
        ingredients = data["ingredients"]
        id_list = []

        for ingredient in ingredients:
            if ingredient["amount"] < settings.MIN_AMOUNT_INGREDIENTS:
                raise ValidationError(settings.AMOUNT_ERROR)
            id_list.append(ingredient.get("id"))

        if len(id_list) == 0:
            raise ValidationError(settings.INGREDIENTS_ERROR)
        if len(tags) == 0 or len(tags) != len(set(tags)):
            raise ValidationError(settings.TAGS_ERROR)
        if cooking_time < settings.COOKING_TIME_MIN:
            raise ValidationError(settings.COOKING_TIME_ERROR)
        return data

    def get_ingredients(self, recipe, ingredients):
        """Method for getting ingredients."""

        models.RecipeIngredient.objects.bulk_create(
            models.RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get("ingredient"),
                amount=ingredient.get("amount")
            ) for ingredient in ingredients)

    @atomic
    def create(self, validated_data):
        """Creation of recipe."""

        user = self.context.get("request").user
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = models.Recipe.objects.create(author=user,
                                              **validated_data)
        recipe.tags.set(tags)
        self.get_ingredients(recipe, ingredients)

        return recipe

    @atomic
    def update(self, instance, validated_data):
        """Update for recipe."""

        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        models.RecipeIngredient.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)
        self.get_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Method for representation recipes."""

        context = {"request": self.context.get("request")}
        return GetRecipeSerializer(instance, context=context).data


class GetRecipeSerializer(serializers.ModelSerializer):
    """Serializer for full information about recipe."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True,
                                             source="recipe_ingredient")
    is_favorited = serializers.SerializerMethodField(
        method_name="get_is_favorited"
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name="get_is_in_shopping_cart"
    )

    class Meta:
        model = models.Recipe
        fields = ("id", "tags", "author", "ingredients",
                  "is_favorited", "is_in_shopping_cart",
                  "name", "image", "text", "cooking_time")

    def get_is_favorited(self, object):
        """Method for getting favorited recipes."""

        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return object.favorite.filter(user=user).exists()

    def get_is_in_shopping_cart(self, object):
        """Method for getting recipes in shoppeng cart."""

        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return object.shopping_cart.filter(user=user).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for adding/deleting recipe to favorite list."""

    class Meta:
        model = models.Favorite
        fields = ("user", "recipe")

    def validate(self, data):
        """Validation."""

        user, recipe = data.get("user"), data.get("recipe")
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(settings.RECIPE_ERROR)
        return data

    def to_representation(self, instance):
        """Method for representation favorite list."""

        context = {"request": self.context.get("request")}
        return BaseRecipeSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(FavoriteSerializer):
    """Serializer for adding/deleting recipe to shoplist."""

    class Meta(FavoriteSerializer.Meta):
        model = models.ShoppingCart
