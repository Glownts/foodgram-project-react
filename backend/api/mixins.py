"""
Mixins and custom viewsets for api app.
"""

from rest_framework import mixins, viewsets


class CreateListRetrievViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Custom viewset for list, create, delete
    and partial update. Does not support the
    PUT method.
    """

    pass
