"""
View-functions.
"""

from django.conf import settings
from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes import models
from users.models import Subscription, User

from . import serializers
from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPagination
from .permissions import AdminOrReadOnly, AuthorAdminOrReadOnly

# -----------------------------------------------------------------------------
#                            Users app
# -----------------------------------------------------------------------------


class UserViewSet(DjoserUserViewSet):
    """
    Viewset for User model.

    Has standart pagination. Any users can gat safe methods.

    Action-methods: "subscription" and "subscribe" - to check
    users subscription, follow and unfollow authors.
    """

    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    http_method_names = ["get", "post", "delete", "head"]

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()

    @action(methods=["POST", "DELETE"],
            detail=True, )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=user, author=author)

        if request.method == "POST":
            if subscription.exists():
                return Response({"error": "Youre alredy subscribed"},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({"error": "Unable to subscribe to yourself"},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = serializers.SubscribeSerializer(
                author,
                context={"request": request}
            )
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"error": "Вы не подписаны на этого пользователя"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        follows = User.objects.filter(following__user=user)
        page = self.paginate_queryset(follows)
        serializer = serializers.SubscribeSerializer(
            page, many=True,
            context={"request": request})
        return self.get_paginated_response(serializer.data)


# -----------------------------------------------------------------------------
#                            Recipe app
# -----------------------------------------------------------------------------


class TagViewSet(ModelViewSet):
    """
    Viewset for Tag model.

    Has no pagination. Only admin can change this model.
    """

    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    """
    Viewset for Ingredient model.

    Has no pagination. Only admin can change this model.
    Has searching by name without register sensitivity.
    """

    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """
    Viewset for Recipe model.

    Has standart pagination. Author and admin can change this model.

    Can be filtred by author, tags, favorites and shopping cart.

    Has method "get_serializer_class" to select serializer by
    http method.
    """

    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    permission_classes = (AuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def action_post_delete(self, pk, serializer_class):
        user = self.request.user
        recipe = get_object_or_404(models.Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )

        if self.request.method == "POST":
            serializer = serializer_class(
                data={"user": user.id, "recipe": pk},
                context={"request": self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == "DELETE":
            if object.exists():
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"error": "This recipe not in list."},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET", "POST", "DELETE"], detail=True)
    def favorite(self, request, pk):
        """Add or delete recipe in favorite list."""

        return self.action_post_delete(pk, serializers.FavoriteSerializer)

    @action(methods=["GET", "POST", "DELETE"], detail=True)
    def shopping_cart(self, request, pk):
        """Add or delete recipe in shop list."""

        return self.action_post_delete(pk, serializers.ShoppingCartSerializer)

    @action(methods=["GET"], detail=False)
    def download_shopping_cart(self, request):
        """Dowload shop list in [FILE_NAME].txt file."""

        user = self.request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = models.RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values(
            name=F("ingredient__name"),
            measurement=F("ingredient__measurement_unit")
        ).annotate(amount=Sum("amount"))

        shopping_list = []

        for units in ingredients:
            shopping_list.append(
                f"{units['name']}: {units['amount']} {units['measurement']}"
            )
        shopping_list = "\n".join(shopping_list)
        response = HttpResponse(
            shopping_list, content_type="text.txt; charset=utf-8"
        )
        response["Content-Disposition"] = ("attachment; "
                                           + f"filename={settings.FILE_NAME}")
        return response
