"""API routing for the cashflow app.

A single DRF ``DefaultRouter`` is mounted under ``/api/`` by the project
URLconf. Later capabilities register their viewsets on ``router`` here with
no further URLconf edits.
"""

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# Viewsets are registered by later changes, e.g.:
#   router.register('records', RecordViewSet)

urlpatterns = router.urls
