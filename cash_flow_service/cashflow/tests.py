"""Smoke tests for the project foundation.

These assert the scaffolding is wired up: the DRF API root responds and the
Django admin serves its login page. No business behavior is exercised here.
"""

import pytest
from django.test import Client


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
