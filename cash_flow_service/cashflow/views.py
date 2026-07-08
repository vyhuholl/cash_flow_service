"""DRF viewsets for the catalog and cash-flow records.

Each dictionary is a ``ModelViewSet`` registered on the ``/api/`` router.
``Category`` and ``Subcategory`` list reads are hierarchy-scoped via ``?type=``
/ ``?category=`` query params so a client can populate dependent dropdowns; an
invalid (non-integer) filter yields an empty list, never a 500. Catalog deletes
trap ``ProtectedError`` and answer HTTP 409 naming the blocking children, so a
protected parent delete — including a catalog row still referenced by a record
— is a clean conflict rather than a server error. ``CashFlowRecord`` exposes
CRUD at ``/api/records/`` plus a filtered, table-ready list: the list action
uses ``CashFlowRecordFilter`` (date period + reference filters), a
label-carrying list serializer, and ``select_related`` to avoid N+1 queries.
Records have no dependents, so any record is freely deletable.
"""

from __future__ import annotations

from typing import Any

from django.db.models import ProtectedError, QuerySet
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from cashflow.filters import CashFlowRecordFilter
from cashflow.models import (
    CashFlowRecord,
    Category,
    Status,
    Subcategory,
    Type,
)
from cashflow.serializers import (
    CashFlowRecordListSerializer,
    CashFlowRecordSerializer,
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


class CashFlowRecordViewSet(viewsets.ModelViewSet):
    # ``select_related`` the reference FKs so the list serializer resolves
    # labels without an extra query per row; model ``Meta.ordering`` already
    # sorts ``-created_date, -id`` for stable pagination.
    queryset = CashFlowRecord.objects.select_related(
        'status', 'type', 'category', 'subcategory'
    )
    serializer_class = CashFlowRecordSerializer
    filterset_class = CashFlowRecordFilter

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == 'list':
            return CashFlowRecordListSerializer
        return CashFlowRecordSerializer
