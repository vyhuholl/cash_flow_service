"""Frontend page routes, mounted at the project root (separate from ``/api/``).

``''`` → home (records table), the record form for create/edit, and the
reference-catalog management page.
"""

from django.urls import path

from cashflow.web import HomeView, RecordFormView, ReferenceView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('records/new', RecordFormView.as_view(), name='record-new'),
    path(
        'records/<int:pk>/edit',
        RecordFormView.as_view(),
        name='record-edit',
    ),
    path('reference', ReferenceView.as_view(), name='reference'),
]
