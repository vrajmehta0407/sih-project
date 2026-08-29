from fastapi.testclient import TestClient
from app.core.config import settings


def test_admin_can_list_users(client: TestClient, admin_token_headers: dict):
    response = client.get(
        f"{settings.API_V1_STR}/users/",
        headers=admin_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] >= 2  # Admin + Inspector seeded


def test_inspector_cannot_list_all_users(client: TestClient, inspector_token_headers: dict):
    response = client.get(
        f"{settings.API_V1_STR}/users/",
        headers=inspector_token_headers
    )
    assert response.status_code == 403  # Forbidden (admin only)


def test_admin_can_register_new_inspector(client: TestClient, admin_token_headers: dict):
    new_inspector = {
        "email": "inspector.pune@legalmetrology.gov.in",
        "password": "SecurePassword@123",
        "full_name": "Suresh Patil",
        "role": "inspector",
        "badge_number": "LM-MH-PUN-109",
        "phone_number": "+91-9988776655",
        "jurisdiction_district": "Pune",
        "jurisdiction_state": "Maharashtra"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/register-inspector",
        headers=admin_token_headers,
        json=new_inspector
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == new_inspector["email"]
    assert data["data"]["badge_number"] == new_inspector["badge_number"]
