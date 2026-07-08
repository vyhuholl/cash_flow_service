"""DRF viewsets for the reference catalog.

Each dictionary is a ``ModelViewSet`` registered on the ``/api/`` router.
``Category`` and ``Subcategory`` list reads are hierarchy-scoped via ``?type=``
/ ``?category=`` query params so a client can populate dependent dropdowns; an
invalid (non-integer) filter yields an empty list, never a 500. Deletes trap
``ProtectedError`` and answer HTTP 409 naming the blocking children, so a
protected parent delete is a clean conflict rather than a server error.
"""

from __future__ import annotations

from typing import Any

from django.db.models import ProtectedError, QuerySet
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from cashflow.models import Category, Status, Subcategory, Type
from cashflow.serializers import (
    CategorySerializer,
    StatusSerializer,
    SubcategorySerializer,
    TypeSerializer,
)


class CatalogViewSet(viewsets.ModelViewSet):
    """Base viewset that answers HTTP 409 on a protected delete.

    Subclasses set ``queryset`` and ``serializer_class`` as usual.
    """

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError as exc:
            blockers = ', '.join(str(obj) for obj in exc.protected_objects)
            return Response(
                {
                    'detail': (
                        'Невозможно удалить, пока есть связанные '
                        f'объекты: {blockers}.'
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class StatusViewSet(CatalogViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer


class TypeViewSet(CatalogViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer


class CategoryViewSet(CatalogViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self) -> QuerySet[Category]:
        queryset = Category.objects.all()
        type_id = self.request.query_params.get('type')
        if type_id is not None:
            if not type_id.isdigit():
                return queryset.none()
            queryset = queryset.filter(type_id=int(type_id))
        return queryset


class SubcategoryViewSet(CatalogViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def get_queryset(self) -> QuerySet[Subcategory]:
        queryset = Subcategory.objects.all()
        category_id = self.request.query_params.get('category')
        if category_id is not None:
            if not category_id.isdigit():
                return queryset.none()
            queryset = queryset.filter(category_id=int(category_id))
        return queryset
