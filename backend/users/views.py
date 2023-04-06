"""
View-functions of user app.
"""

from rest_framework.viewsets import ModelViewSet

from .models import User
from .serializers import UserSerializer
from recipes.permissions import AdminOrReadOnly


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOrReadOnly,)
    