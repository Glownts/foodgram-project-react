"""
Serializers.
"""

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueTogetherValidator

from recipes import models
from users.models import Subscription, User

# -----------------------------------------------------------------------------
#                            Users app
# -----------------------------------------------------------------------------


class UserSerializer(serializers.ModelSerializer):
    """User info."""

    class Meta:
        model = User
        fields = ("__all__",)


class UserCreateSerializer(serializers.ModelSerializer):
    """New user creation."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }


class PasswordSerializer(serializers.Serializer):
    """Allow user changes password."""

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("__all__",)


class SubscribeSerializer(serializers.ModelSerializer):
    """Allow to subscribe to author."""

    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all()
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all()
    )

    def validate(self, data):
        user = data.get("user")
        author = data.get("author")
        if user == author:
            raise serializers.ValidationError("Подписка на себя невозможна!")
        return data

    class Meta:
        fields = ("user", "author")
        model = Subscription
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=("user", "author",),
            )
        ]


class BaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
    """User's subscriptions list."""
    recipes = BaseRecipeSerializer(many=True, required=True)
    is_subscribed = serializers.SerializerMethodField("check_if_is_subscribed")
    recipes_count = serializers.SerializerMethodField("get_recipes_count")

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

    def check_if_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class TokenSerializer(serializers.ModelSerializer):
    """Allow takes token for authorization."""

    token = serializers.CharField(source="key")

    class Meta:
        model = Token
        fields = ("token",)

# -----------------------------------------------------------------------------
#                            Recipe app
# -----------------------------------------------------------------------------


class IngredientSerializer(serializers.ModelSerializer):
    """Show ingredients list."""

    class Meta:
        model = models.Ingredient
        fields = ("__all__",)


class TagSerializer(serializers.ModelSerializer):
    """Show tag list."""

    class Meta:
        model = models.Tag
        fields = ("__all__",)


class FavoriteSerializer(serializers.ModelSerializer):
    """Show recipes in favorite list."""

    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=models.Recipe.objects.all()
    )

    class Meta:
        model = models.Favorite
        fields = ("__all__",)


class ShoppingCartSerializer(FavoriteSerializer):
    """Show recipes in shopping cart."""

    class Meta:
        model = models.ShoppingCart
        fields = ("__all__",)


class IngredientRecipeSerialize(serializers.ModelSerializer):
    """Show ingredients (and amount) in recipes connections (M2M)."""

    id = serializers.ReadOnlyField(source="ingredient.id",)
    name = serializers.ReadOnlyField(source="ingredient.name",)
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = models.IngredientRecipe
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeTag(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=models.Recipe.objects.all()
    )
    tag = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all()
    )

    class Meta:
        model = models.RecipeTag
        fields = ("__all__",)


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """Add ingredients (and amount) in recipes connections."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all()
    )

    class Meta:
        model = models.IngredientRecipe
        fields = ("id", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField("get_ingredients")
    is_favorite = serializers.SerializerMethodField("get_is_favorite")
    is_in_shoplist = serializers.SerializerMethodField("get_is_in_shoplist")

    class Meta:
        model = models.Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorite",
            "is_in_shoplist", "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        ingredients = models.IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeSerialize(ingredients, many=True).data

    def get_is_favorite(self, obj):
        request = self.context.get("request")
        if request in None or request.user.is_anonymus:
            return False
        return models.Favorite.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def get_is_in_shoplist(self, obj):
        request = self.context.get("request")
        if request in None or request.user.is_anonymus:
            return False
        return models.ShoppingCart.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientRecipeSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    cooking_time = serializers.IntegerField()
    tags = serializers.SlugRelatedField(many=True, slug_field="id",
                                        queryset=models.Tag.objects.all())

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
            "cooking_time",
        )

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError("Введите число больше 0")
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        author = self.context.get("request").user
        recipe = models.Recipe.objects.create(author=author, **validated_data)
        for ingredient in ingredients_data:
            ingredients_model = ingredient["id"]
            amount = ingredient["amount"]
            models.IngredientRecipe.objects.create(
                ingredient=ingredients_model, recipe=recipe, amount=amount
            )
            recipe.tags.set(tags_data)
            return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        models.RecipeTag.objects.filter(recipe=instance).delete()
        models.IngredientRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients_data:
            ingredient_model = ingredient["id"]
            amount = ingredient["amount"]
            models.IngredientRecipe.objects.create(
                ingredient=ingredient_model, recipe=instance, amount=amount
            )
        instance.name = validated_data.pop("name")
        instance.text = validated_data.pop("text")
        if validated_data.get("image") is not None:
            instance.image = validated_data.pop("image")
        instance.cooking_time = validated_data.pop("cooking_time")
        instance.tags.set(tags_data)
        instance.save()
        return instance
