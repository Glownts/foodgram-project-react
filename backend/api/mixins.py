"""
Mixins and custom viewsets for api app.
"""

from rest_framework import serializers, response, status
from django.db.models import Q
from django.shortcuts import get_object_or_404


class M2MMixin:
    """
    Custom viewset with additional methods.

    Contains method that allow to add/delete objects
    wit M2M connections.

    Requires the `add_serializer` attribute to be defined.
    """

    add_serializer: serializers.ModelSerializer | None = None

    def _add_del_obj(self, obj_id, m2m_model, q):
        """Add or delete M2M connection."""

        obj = get_object_or_404(self.queryset, id=obj_id)
        serializer = self.add_serializer(obj)
        m2m = m2m_model.objects.filter(q & Q(user=self.request.user))

        if not m2m:
            if (self.request.method in ("GET", "POST",)):
                m2m_model(None, obj.id, self.request.user.id).save()
                return response.Response(serializer.data,
                                         status=status.HTTP_201_CREATED)

        if m2m:
            if (self.request.method == "DELETE"):
                m2m[0].delete()
                return response.Response(status=status.HTTP_204_NO_CONTENT)

        return response.Response(status=status.HTTP_400_BAD_REQUEST)
