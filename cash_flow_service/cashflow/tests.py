"""Tests for the project foundation and the reference catalog.

The smoke tests assert the scaffolding is wired up (DRF root, admin login).
The catalog tests exercise the dictionaries' uniqueness rules, PROTECT-on-
delete behavior, and hierarchy-scoped list reads through the REST API.
"""

import pytest
from django.test import Client
from rest_framework import status as http_status
from rest_framework.test import APIClient

from cashflow.models import Category, Status, Subcategory, Type


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
