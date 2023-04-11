"""
View-functions.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum, Q, F
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes import models
from users.models import Subscription

from . import serializers
from .filters import RecipeFilter
from .mixins import M2MMixin
from .permissions import AdminOrReadOnly, AuthorAdminOrReadOnly
# from rest_framework.routers import APIRootView


# -----------------------------------------------------------------------------
#                            Users app
# -----------------------------------------------------------------------------

User = get_user_model()


class UserViewSet(DjoserUserViewSet, M2MMixin):
    """
    Viewset for User model.

    Has standart pagination. Any users can gat safe methods.

    Action-methods: "subscription" and "subscribe" - to check
    user's subscription, follow and unfollow authors.
    """

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    add_serializer = serializers.SubscribeSerializer
    pagination_class = PageNumberPagination

    # @action(methods=["get"], detail=False,
    #         pagination_class=None,
    #         permission_classes=[IsAuthenticated])
    # def me(self, request):
    #     """Defines current user."""

    #     serializer = serializers.UserSerializer(request.user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(methods=["post"], detail=False,
    #         permission_classes=[IsAuthenticated])
    # def set_password(self, request):
    #     """Allows users to change their passwords."""

    #     serializer = serializers.PasswordSerializer(request.user,
    #                                                 data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({'detail': 'Пароль успешно изменен!'},
    #                         status=status.HTTP_204_NO_CONTENT)
    #     return Response(
    # serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=False,
            permission_classes=[IsAuthenticated],
            pagination_class=PageNumberPagination)
    def subscriptions(self, request):
        """Shows user's subscriptions."""

        subscriptions = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(subscriptions)
        serializer = serializers.SubscribeSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=["post", "delete"], detail=False,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Allows the user to follow and unfollow authors."""

        return self._add_del_obj(id, Subscription, Q(author__id=id))

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


class RecipeViewSet(ModelViewSet, M2MMixin):
    """
    Viewset for Recipe model.

    Has standart pagination. Author and admin can change this model.

    Can be filtred by author, tags, favorites and shopping cart.

    Has method "get_serializer_class" to select serializer by
    http method.
    """

    queryset = models.Recipe.objects.select_related("author")
    serializer_class = serializers.RecipeSerializer
    permission_classes = (AuthorAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination
    add_serializer = serializers.BaseRecipeSerializer

    @action(methods=['GET', 'POST', 'DELETE'], detail=False,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Add or delete recipe in favorite list."""

        return self._add_del_obj(pk, models.Favorite, Q(recipe__id=pk))

    @action(methods=['GET', 'POST', 'DELETE'], detail=False,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Add or delete recipe in shop list."""

        return self._add_del_obj(pk, models.ShoppingCart, Q(recipe__id=pk))

    @action(methods=['GET'], detail=False)
    def download_shopping_cart(self, request):
        """Dowload shop list in [FILE_NAME].txt file."""

        user = self.request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = models.Ingredient.objects.filter(
            recipe__recipe__recipe_in_shopping_cart__user=user
        ).values(
            'name',
            measurement=F('measurement_unit')
        ).annotate(amount=Sum('recipe__amount'))

        shopping_list = []

        for units in ingredients:
            shopping_list.append(
                f'{units["name"]}: {units["amount"]} {units["measurement"]}'
            )

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = ('attachment; '
                                           + f'filename={settings.FILE_NAME}')
        return response
