"""Tests for the project foundation, the reference catalog, and records.

The smoke tests assert the scaffolding is wired up (DRF root, admin login).
The catalog tests exercise the dictionaries' uniqueness rules, PROTECT-on-
delete behavior, and hierarchy-scoped list reads. The record tests cover
required fields, positive amount, the date default/override, the two hierarchy
business rules, and PROTECT of catalog rows referenced by a record. The
list-filtering tests cover the date-period and reference filters, their AND
composition, newest-first ordering, pagination, resolved label fields, and the
absence of N+1 queries — all through the REST API.
"""

from datetime import date
from decimal import Decimal
from typing import Any

import pytest
from django.test import Client
from rest_framework import status as http_status
from rest_framework.test import APIClient

from cashflow.models import (
    CashFlowRecord,
    Category,
    Status,
    Subcategory,
    Type,
)


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_api_root_responds(client: Client) -> None:
    """The DRF router root under /api/ returns HTTP 200."""
    response = client.get('/api/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_serves_login_page(client: Client) -> None:
    """GET /admin/ redirects to and serves the admin login page."""
    response = client.get('/admin/', follow=True)
    assert response.status_code == 200
    assert b'name="username"' in response.content


# --- Uniqueness (task 5.1) -------------------------------------------------


@pytest.mark.django_db
def test_duplicate_status_name_rejected(api: APIClient) -> None:
    Status.objects.create(name='Бизнес')
    response = api.post('/api/statuses/', {'name': 'Бизнес'})
    assert response.status_code == http_status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_duplicate_type_name_rejected(api: APIClient) -> None:
    Type.objects.create(name='Списание')
    response = api.post('/api/types/', {'name': 'Списание'})
    assert response.status_code == http_status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_category_name_unique_within_type(api: APIClient) -> None:
    spisanie = Type.objects.create(name='Списание')
    popolnenie = Type.objects.create(name='Пополнение')
    Category.objects.create(name='Маркетинг', type=spisanie)

    duplicate = api.post(
        '/api/categories/', {'name': 'Маркетинг', 'type': spisanie.id}
    )
    assert duplicate.status_code == http_status.HTTP_400_BAD_REQUEST

    other_type = api.post(
        '/api/categories/', {'name': 'Маркетинг', 'type': popolnenie.id}
    )
    assert other_type.status_code == http_status.HTTP_201_CREATED


@pytest.mark.django_db
def test_subcategory_name_unique_within_category(api: APIClient) -> None:
    type_ = Type.objects.create(name='Списание')
    marketing = Category.objects.create(name='Маркетинг', type=type_)
    sales = Category.objects.create(name='Продажи', type=type_)
    Subcategory.objects.create(name='Farpost', category=marketing)

    duplicate = api.post(
        '/api/subcategories/', {'name': 'Farpost', 'category': marketing.id}
    )
    assert duplicate.status_code == http_status.HTTP_400_BAD_REQUEST

    other_category = api.post(
        '/api/subcategories/', {'name': 'Farpost', 'category': sales.id}
    )
    assert other_category.status_code == http_status.HTTP_201_CREATED


# --- PROTECT on delete (task 5.2) ------------------------------------------


@pytest.mark.django_db
def test_delete_category_with_subcategories_returns_409(
    api: APIClient,
) -> None:
    type_ = Type.objects.create(name='Списание')
    category = Category.objects.create(name='Маркетинг', type=type_)
    Subcategory.objects.create(name='Farpost', category=category)

    response = api.delete(f'/api/categories/{category.id}/')
    assert response.status_code == http_status.HTTP_409_CONFLICT
    assert Category.objects.filter(pk=category.pk).exists()


@pytest.mark.django_db
def test_delete_childless_subcategory_succeeds(api: APIClient) -> None:
    type_ = Type.objects.create(name='Списание')
    category = Category.objects.create(name='Маркетинг', type=type_)
    subcategory = Subcategory.objects.create(name='Farpost', category=category)

    response = api.delete(f'/api/subcategories/{subcategory.id}/')
    assert response.status_code == http_status.HTTP_204_NO_CONTENT
    assert not Subcategory.objects.filter(pk=subcategory.pk).exists()


# --- Hierarchy-scoped reads (task 5.3) -------------------------------------


@pytest.mark.django_db
def test_categories_filtered_by_type(api: APIClient) -> None:
    spisanie = Type.objects.create(name='Списание')
    popolnenie = Type.objects.create(name='Пополнение')
    Category.objects.create(name='Маркетинг', type=spisanie)
    Category.objects.create(name='Продажи', type=popolnenie)

    response = api.get(f'/api/categories/?type={spisanie.id}')
    assert response.status_code == 200
    names = [row['name'] for row in response.data['results']]
    assert names == ['Маркетинг']


@pytest.mark.django_db
def test_categories_invalid_type_filter_is_empty(api: APIClient) -> None:
    type_ = Type.objects.create(name='Списание')
    Category.objects.create(name='Маркетинг', type=type_)

    response = api.get('/api/categories/?type=abc')
    assert response.status_code == 200
    assert response.data['results'] == []


@pytest.mark.django_db
def test_subcategories_filtered_by_category(api: APIClient) -> None:
    type_ = Type.objects.create(name='Списание')
    marketing = Category.objects.create(name='Маркетинг', type=type_)
    sales = Category.objects.create(name='Продажи', type=type_)
    Subcategory.objects.create(name='Farpost', category=marketing)
    Subcategory.objects.create(name='Avito', category=sales)

    response = api.get(f'/api/subcategories/?category={marketing.id}')
    assert response.status_code == 200
    names = [row['name'] for row in response.data['results']]
    assert names == ['Farpost']


# --- Cash-flow records -----------------------------------------------------


def _make_catalog() -> dict[str, Any]:
    """A consistent Тип → Категория → Подкатегория chain plus a status."""
    type_ = Type.objects.create(name='Списание')
    category = Category.objects.create(name='Маркетинг', type=type_)
    subcategory = Subcategory.objects.create(name='Farpost', category=category)
    status = Status.objects.create(name='Бизнес')
    return {
        'type': type_,
        'category': category,
        'subcategory': subcategory,
        'status': status,
    }


def _valid_payload(catalog: dict[str, Any]) -> dict[str, Any]:
    """A minimal valid create payload for the given catalog chain."""
    return {
        'type': catalog['type'].id,
        'category': catalog['category'].id,
        'subcategory': catalog['subcategory'].id,
        'amount': '100.50',
    }


@pytest.mark.django_db
def test_record_full_crud_lifecycle(api: APIClient) -> None:
    catalog = _make_catalog()

    created = api.post('/api/records/', _valid_payload(catalog))
    assert created.status_code == http_status.HTTP_201_CREATED
    record_id = created.data['id']

    assert api.get(f'/api/records/{record_id}/').status_code == 200

    patched = api.patch(f'/api/records/{record_id}/', {'amount': '250.00'})
    assert patched.status_code == 200
    assert patched.data['amount'] == '250.00'

    deleted = api.delete(f'/api/records/{record_id}/')
    assert deleted.status_code == http_status.HTTP_204_NO_CONTENT
    assert not CashFlowRecord.objects.filter(pk=record_id).exists()


# --- Required fields (task 5.1) --------------------------------------------


@pytest.mark.django_db
def test_record_requires_amount_type_category_subcategory(
    api: APIClient,
) -> None:
    response = api.post('/api/records/', {})
    assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    for field in ('amount', 'type', 'category', 'subcategory'):
        assert field in response.data
    for optional in ('status', 'created_date', 'comment'):
        assert optional not in response.data


@pytest.mark.django_db
def test_record_created_without_status_or_comment(api: APIClient) -> None:
    catalog = _make_catalog()
    response = api.post('/api/records/', _valid_payload(catalog))
    assert response.status_code == http_status.HTTP_201_CREATED
    assert response.data['status'] is None
    assert response.data['comment'] == ''


# --- Amount and date (task 5.2) --------------------------------------------


@pytest.mark.django_db
def test_record_rejects_non_positive_amount(api: APIClient) -> None:
    catalog = _make_catalog()
    payload = _valid_payload(catalog)
    payload['amount'] = '0'
    response = api.post('/api/records/', payload)
    assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    assert 'amount' in response.data


@pytest.mark.django_db
def test_record_date_defaults_to_today(api: APIClient) -> None:
    catalog = _make_catalog()
    response = api.post('/api/records/', _valid_payload(catalog))
    assert response.status_code == http_status.HTTP_201_CREATED
    assert response.data['created_date'] == date.today().isoformat()


@pytest.mark.django_db
def test_record_date_can_be_overridden(api: APIClient) -> None:
    catalog = _make_catalog()
    payload = _valid_payload(catalog)
    payload['created_date'] = '2025-01-01'
    response = api.post('/api/records/', payload)
    assert response.status_code == http_status.HTTP_201_CREATED
    assert response.data['created_date'] == '2025-01-01'


# --- Hierarchy business rules (task 5.3) -----------------------------------


@pytest.mark.django_db
def test_record_rejects_category_not_in_type(api: APIClient) -> None:
    catalog = _make_catalog()
    other_type = Type.objects.create(name='Пополнение')
    payload = _valid_payload(catalog)
    payload['type'] = other_type.id
    response = api.post('/api/records/', payload)
    assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    assert 'category' in response.data


@pytest.mark.django_db
def test_record_rejects_subcategory_not_in_category(
    api: APIClient,
) -> None:
    catalog = _make_catalog()
    other_category = Category.objects.create(
        name='Продажи', type=catalog['type']
    )
    payload = _valid_payload(catalog)
    payload['category'] = other_category.id
    response = api.post('/api/records/', payload)
    assert response.status_code == http_status.HTTP_400_BAD_REQUEST
    assert 'subcategory' in response.data


@pytest.mark.django_db
def test_record_accepts_consistent_hierarchy(api: APIClient) -> None:
    catalog = _make_catalog()
    response = api.post('/api/records/', _valid_payload(catalog))
    assert response.status_code == http_status.HTTP_201_CREATED


# --- PROTECT of referenced catalog rows (task 5.4) -------------------------


@pytest.mark.django_db
def test_referenced_catalog_rows_cannot_be_deleted(api: APIClient) -> None:
    catalog = _make_catalog()
    payload = _valid_payload(catalog)
    payload['status'] = catalog['status'].id
    assert (
        api.post('/api/records/', payload).status_code
        == http_status.HTTP_201_CREATED
    )

    for kind, obj in (
        ('statuses', catalog['status']),
        ('types', catalog['type']),
        ('categories', catalog['category']),
        ('subcategories', catalog['subcategory']),
    ):
        response = api.delete(f'/api/{kind}/{obj.id}/')
        assert response.status_code == http_status.HTTP_409_CONFLICT, kind


# --- Records list filtering ------------------------------------------------


def _seed_catalog() -> dict[str, Any]:
    """Two independent Тип → Категория → Подкатегория chains and statuses."""
    t1 = Type.objects.create(name='Списание')
    t2 = Type.objects.create(name='Пополнение')
    c1 = Category.objects.create(name='Маркетинг', type=t1)
    c2 = Category.objects.create(name='Продажи', type=t2)
    s1 = Subcategory.objects.create(name='Farpost', category=c1)
    s2 = Subcategory.objects.create(name='Avito', category=c2)
    st1 = Status.objects.create(name='Бизнес')
    st2 = Status.objects.create(name='Личное')
    return {
        't1': t1,
        't2': t2,
        'c1': c1,
        'c2': c2,
        's1': s1,
        's2': s2,
        'st1': st1,
        'st2': st2,
    }


def _seed_records(cat: dict[str, Any]) -> dict[str, Any]:
    """Three records spanning three months, types, and statuses."""
    r1 = CashFlowRecord.objects.create(
        created_date=date(2025, 1, 1),
        type=cat['t1'],
        category=cat['c1'],
        subcategory=cat['s1'],
        status=cat['st1'],
        amount=Decimal('100.00'),
    )
    r2 = CashFlowRecord.objects.create(
        created_date=date(2025, 2, 15),
        type=cat['t1'],
        category=cat['c1'],
        subcategory=cat['s1'],
        status=None,
        amount=Decimal('200.00'),
    )
    r3 = CashFlowRecord.objects.create(
        created_date=date(2025, 3, 20),
        type=cat['t2'],
        category=cat['c2'],
        subcategory=cat['s2'],
        status=cat['st2'],
        amount=Decimal('300.00'),
    )
    return {'r1': r1, 'r2': r2, 'r3': r3}


def _ids(response: Any) -> list[int]:
    return [row['id'] for row in response.data['results']]


# --- Individual filters (task 4.1) -----------------------------------------


@pytest.mark.django_db
def test_filter_by_bounded_date_period(api: APIClient) -> None:
    cat = _seed_catalog()
    recs = _seed_records(cat)
    response = api.get('/api/records/?date_from=2025-02-01&date_to=2025-03-01')
    assert response.status_code == 200
    assert _ids(response) == [recs['r2'].id]


@pytest.mark.django_db
def test_filter_by_open_ended_date_from(api: APIClient) -> None:
    cat = _seed_catalog()
    recs = _seed_records(cat)
    response = api.get('/api/records/?date_from=2025-02-01')
    assert _ids(response) == [recs['r3'].id, recs['r2'].id]


@pytest.mark.django_db
def test_filter_by_open_ended_date_to(api: APIClient) -> None:
    cat = _seed_catalog()
    recs = _seed_records(cat)
    response = api.get('/api/records/?date_to=2025-01-31')
    assert _ids(response) == [recs['r1'].id]


@pytest.mark.django_db
def test_filter_by_status(api: APIClient) -> None:
    cat = _seed_catalog()
    recs = _seed_records(cat)
    response = api.get(f'/api/records/?status={cat["st1"].id}')
    assert _ids(response) == [recs['r1'].id]


@pytest.mark.django_db
def test_filter_by_type(api: APIClient) -> None:
    cat = _seed_catalog()
    recs = _seed_records(cat)
    response = api.get(f'/api/records/?type={cat["t1"].id}')
    assert _ids(response) == [recs['r2'].id, recs['r1'].id]


@pytest.mark.django_db
def test_filter_by_category(api: APIClient) -> None:
    cat = _seed_catalog()
    recs = _seed_records(cat)
    response = api.get(f'/api/records/?category={cat["c2"].id}')
    assert _ids(response) == [recs['r3'].id]


@pytest.mark.django_db
def test_filter_by_subcategory(api: APIClient) -> None:
    cat = _seed_catalog()
    recs = _seed_records(cat)
    response = api.get(f'/api/records/?subcategory={cat["s1"].id}')
    assert _ids(response) == [recs['r2'].id, recs['r1'].id]


# --- Composition and defaults (task 4.2) -----------------------------------


@pytest.mark.django_db
def test_combined_filters_use_and_semantics(api: APIClient) -> None:
    cat = _seed_catalog()
    recs = _seed_records(cat)
    response = api.get(
        f'/api/records/?type={cat["t1"].id}'
        f'&status={cat["st1"].id}&date_from=2024-12-01'
    )
    assert _ids(response) == [recs['r1'].id]


@pytest.mark.django_db
def test_no_filter_returns_all(api: APIClient) -> None:
    cat = _seed_catalog()
    _seed_records(cat)
    response = api.get('/api/records/')
    assert response.data['count'] == 3
    assert len(response.data['results']) == 3


# --- Ordering and pagination (task 4.3) ------------------------------------


@pytest.mark.django_db
def test_default_ordering_is_newest_first(api: APIClient) -> None:
    cat = _seed_catalog()
    recs = _seed_records(cat)
    response = api.get('/api/records/')
    assert _ids(response) == [recs['r3'].id, recs['r2'].id, recs['r1'].id]
    dates = [row['created_date'] for row in response.data['results']]
    assert dates == ['2025-03-20', '2025-02-15', '2025-01-01']


@pytest.mark.django_db
def test_pagination_splits_large_result_set(api: APIClient) -> None:
    cat = _seed_catalog()
    for _ in range(26):
        CashFlowRecord.objects.create(
            created_date=date(2025, 1, 1),
            type=cat['t1'],
            category=cat['c1'],
            subcategory=cat['s1'],
            amount=Decimal('10.00'),
        )
    page1 = api.get('/api/records/')
    assert page1.data['count'] == 26
    assert len(page1.data['results']) == 25
    assert page1.data['next'] is not None

    page2 = api.get('/api/records/?page=2')
    assert len(page2.data['results']) == 1
    assert page2.data['previous'] is not None


# --- Table-ready rows and N+1 (task 4.4) -----------------------------------


@pytest.mark.django_db
def test_rows_carry_resolved_labels(api: APIClient) -> None:
    cat = _seed_catalog()
    recs = _seed_records(cat)
    response = api.get('/api/records/')
    rows = {row['id']: row for row in response.data['results']}

    r1 = rows[recs['r1'].id]
    assert r1['type_name'] == 'Списание'
    assert r1['category_name'] == 'Маркетинг'
    assert r1['subcategory_name'] == 'Farpost'
    assert r1['status_name'] == 'Бизнес'
    assert r1['amount'] == '100.00'
    assert r1['comment'] == ''

    # A null status resolves to a null label rather than erroring.
    r2 = rows[recs['r2'].id]
    assert r2['status'] is None
    assert r2['status_name'] is None


@pytest.mark.django_db
def test_list_avoids_n_plus_one_queries(
    api: APIClient, django_assert_max_num_queries: Any
) -> None:
    cat = _seed_catalog()
    _seed_records(cat)
    for _ in range(5):
        CashFlowRecord.objects.create(
            created_date=date(2025, 4, 1),
            type=cat['t1'],
            category=cat['c1'],
            subcategory=cat['s1'],
            status=cat['st1'],
            amount=Decimal('50.00'),
        )
    # select_related folds every label into the page query, so the query
    # count stays constant (page + COUNT) no matter how many rows come back.
    with django_assert_max_num_queries(3):
        response = api.get('/api/records/')
    assert response.status_code == 200


# --- Frontend page shells (task 5.1) ---------------------------------------


@pytest.mark.django_db
def test_home_page_renders_shell(client: Client) -> None:
    response = client.get('/')
    assert response.status_code == 200
    content = response.content.decode()
    assert 'Записи ДДС' in content
    assert 'id="records-body"' in content
    # ensure_csrf_cookie set the cookie the fetch helper echoes back.
    assert 'csrftoken' in response.cookies


@pytest.mark.django_db
def test_record_new_page_renders_shell(client: Client) -> None:
    response = client.get('/records/new')
    assert response.status_code == 200
    content = response.content.decode()
    assert 'id="record-form"' in content
    assert '"recordId": null' in content


@pytest.mark.django_db
def test_record_edit_page_embeds_record_id(client: Client) -> None:
    response = client.get('/records/7/edit')
    assert response.status_code == 200
    # The pk is embedded so the client-side loader fetches that record.
    assert '"recordId": 7' in response.content.decode()


@pytest.mark.django_db
def test_reference_page_renders_shell(client: Client) -> None:
    response = client.get('/reference')
    assert response.status_code == 200
    content = response.content.decode()
    assert 'Справочники' in content
    for dictionary in ('statuses', 'types', 'categories', 'subcategories'):
        assert f'data-dict="{dictionary}"' in content
