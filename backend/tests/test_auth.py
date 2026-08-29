from fastapi.testclient import TestClient
from app.core.config import settings


def test_health_endpoint(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == settings.PROJECT_NAME


def test_admin_login_success(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["email"] == settings.FIRST_SUPERUSER_EMAIL


def test_inspector_login_json(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login/json",
        json={
            "email": settings.FIRST_INSPECTOR_EMAIL,
            "password": settings.FIRST_INSPECTOR_PASSWORD
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "inspector"


def test_invalid_login_fails(client: TestClient):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={
            "username": "wrong.user@legalmetrology.gov.in",
            "password": "WrongPassword!999"
        }
    )
    assert response.status_code == 401


def test_get_current_user_profile(client: TestClient, inspector_token_headers: dict):
    response = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers=inspector_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == settings.FIRST_INSPECTOR_EMAIL
    assert data["data"]["role"] == "inspector"
    assert data["data"]["jurisdiction_state"] == "Maharashtra"
