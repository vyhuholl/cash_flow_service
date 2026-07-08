"""API routing for the cashflow app.

A single DRF ``DefaultRouter`` is mounted under ``/api/`` by the project
URLconf. Later capabilities register their viewsets on ``router`` here with
no further URLconf edits.
"""

from rest_framework.routers import DefaultRouter

from cashflow.views import (
    CategoryViewSet,
    StatusViewSet,
    SubcategoryViewSet,
    TypeViewSet,
)

router = DefaultRouter()
router.register('statuses', StatusViewSet)
router.register('types', TypeViewSet)
router.register('categories', CategoryViewSet)
router.register('subcategories', SubcategoryViewSet)

urlpatterns = router.urls
