from fastapi.testclient import TestClient
from app.core.config import settings


def test_get_active_rule_version(client: TestClient, inspector_token_headers: dict):
    response = client.get(
        f"{settings.API_V1_STR}/rules/active",
        headers=inspector_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["version_tag"] == "LM-PCR-2011-V1.0-NATIONAL"
    assert len(data["data"]["rules"]) >= 8


def test_list_rules_with_statutory_citations(client: TestClient, inspector_token_headers: dict):
    response = client.get(
        f"{settings.API_V1_STR}/rules/",
        headers=inspector_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    rules = data["data"]
    assert len(rules) >= 8

    # Verify statutory citations
    rule_codes = [r["rule_code"] for r in rules]
    assert "LM_RULE_6_1_E_MRP" in rule_codes
    assert "LM_RULE_6_1_C_NET_QTY" in rule_codes
    assert "LM_RULE_6_1_A_MFG_DETAILS" in rule_codes
    assert "LM_RULE_6_1_D_MFG_DATE" in rule_codes
    assert "LM_RULE_6_1_G_COUNTRY_OF_ORIGIN" in rule_codes

    # Check that Section 18 / Section 36 / Rule 6 citations are present
    mrp_rule = next(r for r in rules if r["rule_code"] == "LM_RULE_6_1_E_MRP")
    assert "Rule 6(1)(e)" in mrp_rule["statutory_source"]
    assert "Section 36" in mrp_rule["statutory_penalty_source"]
