"""
View-functions.
"""

from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from recipes import models
from users.models import Subscription, User

from . import serializers
from .filters import RecipeFilter
from .mixins import CreateListRetrievViewSet
from .permissions import AdminOrReadOnly, AuthorAdminOrReadOnly

# -----------------------------------------------------------------------------
#                            Users app
# -----------------------------------------------------------------------------


class UserViewSet(CreateListRetrievViewSet):
    """
    Viewset for User model.

    Has standart pagination. Any users can gat safe methods.

    Has four action-methods: "me" - to define current user,
    "set_password" - allow users to change their passwords,
    "subscription" and "subscribe" - to check user's subscription,
    follow or unfollow authors.
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """Defines which serializer need to use."""

        if self.request.method == "GET":
            return serializers.UserSerializer
        return serializers.UserCreateSerializer

    @action(methods=["get"], detail=False,
            pagination_class=None,
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Defines current user."""

        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False,
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        """Allows users to change their passwords."""

        serializer = serializers.PasswordSerializer(request.user,
                                                    data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Пароль успешно изменен!'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=False,
            permission_classes=[IsAuthenticated],
            pagination_class=PageNumberPagination)
    def subscriptions(self, request):
        """Shows user's subscriptions."""

        subscriptions = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = serializers.SubscriptionsSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=["post", "delete"], detail=False,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Allows the user to follow and unfollow authors."""

        author = get_object_or_404(User, id=kwargs["pk"])

        if request.method == 'POST':
            serializer = serializers.SubscribeSerializer(
                author,
                data=request.data,
                context={"request": request}
            )
            if serializer.is_valid():
                Subscription.objects.create(user=request.user, author=author)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=request.user,
                              author=author).delete()
            return Response({'detail': 'Вы успешно отказались от подписки'},
                            status=status.HTTP_204_NO_CONTENT)

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
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ("^name",)


class RecipeViewSet(ModelViewSet):
    """
    Viewset for Recipe model.

    Has standart pagination. Author and admin can change this model.

    Can be filtred by author, tags, favorites and shopping cart.

    Has method "get_serializer_class" to select serializer by
    http method.
    """

    queryset = models.Recipe.objects.all()
    permission_classes = (AuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        """Defines which serializer need to use."""

        if self.request.method in ("POST", "PATCH",):
            return serializers.RecipeCreateSerializer
        return serializers.RecipeSerializer

    def get_serializer_context(self):
        """Add serializer's context."""

        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class FavoriteViewSet(APIView):
    """
    Viewset for Favorite model.

    Has no pagination. Only authenticated users can change this model.

    Has action method "favorite" to add and delete recipes from favorite.
    """

    permission_classes = (IsAuthenticated,)
    pagination_class = None

    @action(detail=True, methods=["post", "delete"])
    def favorite(self, request, **kwargs):
        """Add or delete recipe in favorite list."""

        recipe = get_object_or_404(models.Recipe, id=kwargs["pk"])

        if request.method == "POST":
            serializer = serializers.FavoriteSerializer(
                data=request.data,
                context={"request": request}
            )
            if serializer.is_valid():
                if not models.Favorite.objects.filter(user=request.user,
                                                      recipe=recipe).exists():
                    models.Favorite.objects.create(user=request.user,
                                                   recipe=recipe)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
            return Response({"errors": "Рецепт уже в избранном."},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == "DELETE":
            get_object_or_404(models.Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response({"detail": "Рецепт успешно удален из избранного"},
                            status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(APIView):
    """
    Viewset for ShoppingCart model.

    Has no pagination. Only authenticated users can change this model.

    Has two action-methods: "shopping_cart" to add and delete recipes from
    shopping list and "download_shopping_cart" to download recipes's
    ingredients in .txt file.
    """

    permission_classes = (IsAuthenticated,)
    pagination_class = None

    @action(detail=True, methods=["post", "delete"])
    def shopping_cart(self, request, **kwargs):
        """Add or delete recipe in shoplist."""

        recipe = get_object_or_404(models.Recipe, id=kwargs["pk"])

        if request.method == "POST":
            serializer = serializers.ShoppingCartSerializer(
                recipe, data=request.data,
                context={"request": request}
            )
            if serializer.is_valid():
                if not models.ShoppingCart.objects.filter(
                    user=request.user,
                    recipe=recipe
                ).exists():
                    models.ShoppingCart.objects.create(user=request.user,
                                                       recipe=recipe)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
            return Response({"errors": "Рецепт уже в списке покупок."},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == "DELETE":
            get_object_or_404(models.ShoppingCart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {"detail": "Рецепт успешно удален из списка покупок"},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=["get"])
    def download_shopping_cart(self, request, **kwargs):
        """Download shoplist in .txt format."""

        ingredients = (
            models.IngredientRecipe.objects
            .filter(recipe__recipe_in_shopping_cart__user=request.user)
            .values("ingredient")
            .annotate(total_amount=Sum("amount"))
            .values_list("ingredient__name", "total_amount",
                         "ingredient__measurement_unit")
        )
        file_list = []
        [file_list.append(
            "{} - {} {}.".format(*ingredient)) for ingredient in ingredients]
        file = HttpResponse(
            "Списко покупок:\n" + "\n".join(file_list),
            content_type="text/plain"
        )
        file["Content-Disposition"] = (
            f"attachment; filename={settings.FILE_NAME}"
        )
        return file
