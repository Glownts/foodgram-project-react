"""
View-functions of recipe app.
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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .filters import RecipeFilter
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)
from .permissions import AdminOrReadOnly, AuthorAdminOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagViewSet(ModelViewSet):
    """
    Viewset for Tag model.

    Has no pagination. Only admin can change this model.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    """
    Viewset for Ingredient model.

    Has no pagination. Only admin can change this model.
    Has searching by name without register sensitivity.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
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
    queryset = Recipe.objects.all()
    permission_classes = (AuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in ("POST", "PATCH",):
            return RecipeCreateSerializer
        return RecipeSerializer

    def get_serializer_context(self):
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
        recipe = get_object_or_404(Recipe, id=kwargs["pk"])

        if request.method == "POST":
            serializer = FavoriteSerializer(data=request.data,
                                            context={"request": request})
            if serializer.is_valid():
                if not Favorite.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                    serializer.save()
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
            return Response({"errors": "Рецепт уже в избранном."},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == "DELETE":
            get_object_or_404(Favorite, user=request.user,
                              recipe=recipe).delete()
            return Response({"detail": "Рецепт успешно удален из избранного"},
                            status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(APIView):
    """
    Viewset for ShoppingCart model.

    Has no pagination. Only authenticated users can change this model.

    Has two action methods "shopping_cart" to add and delete recipes from
    shopping list and "download_shopping_cart" to download recipes's
    ingredients in .txt file.
    """
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    @action(detail=True, methods=["post", "delete"])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs["pk"])

        if request.method == "POST":
            serializer = ShoppingCartSerializer(recipe, data=request.data,
                                                context={"request": request})
            if serializer.is_valid():
                if not ShoppingCart.objects.filter(user=request.user,
                                                   recipe=recipe).exists():
                    serializer.save()
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
            return Response({"errors": "Рецепт уже в списке покупок."},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == "DELETE":
            get_object_or_404(ShoppingCart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {"detail": "Рецепт успешно удален из списка покупок"},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(detail=False, methods=["get"])
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            IngredientRecipe.objects
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
