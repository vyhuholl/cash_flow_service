"""Filter set for the cash-flow records list endpoint.

Backs the главная страница table: an inclusive ``date_from``/``date_to`` period
over ``created_date`` plus exact-match filters on the four reference fields.
Any subset composes with AND semantics; an empty query returns everything.
django-filter also renders the filter form in the browsable API.
"""

import django_filters

from cashflow.models import CashFlowRecord


class CashFlowRecordFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(
        field_name='created_date', lookup_expr='gte'
    )
    date_to = django_filters.DateFilter(
        field_name='created_date', lookup_expr='lte'
    )

    class Meta:
        model = CashFlowRecord
        fields = ['status', 'type', 'category', 'subcategory']
