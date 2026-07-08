"""Server-rendered page shells for the cash-flow frontend.

Thin ``TemplateView``s that return HTML only; all data and mutations happen
client-side against the ``/api/`` endpoints via ``fetch``. Each view is wrapped
with ``ensure_csrf_cookie`` so the ``csrftoken`` cookie is present for the JS
helper to echo back in the ``X-CSRFToken`` header on unsafe requests.
"""

from typing import Any

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView


@method_decorator(ensure_csrf_cookie, name='dispatch')
class HomeView(TemplateView):
    template_name = 'cashflow/records_list.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class RecordFormView(TemplateView):
    template_name = 'cashflow/record_form.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # ``pk`` is present on the edit route, absent on ``records/new``; the
        # template embeds it so the client-side loader knows which record (if
        # any) to fetch and pre-fill.
        context['record_id'] = kwargs.get('pk')
        return context


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ReferenceView(TemplateView):
    template_name = 'cashflow/reference.html'
