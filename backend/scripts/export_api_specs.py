import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

def export_specs():
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs")
    os.makedirs(docs_dir, exist_ok=True)

    # 1. Export OpenAPI 3.1 JSON Specification
    openapi_schema = app.openapi()
    openapi_path = os.path.join(docs_dir, "openapi_spec.json")
    with open(openapi_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"[OK] Exported OpenAPI 3.1 Schema: {openapi_path}")

    # 2. Build Postman Collection v2.1
    postman_collection = {
        "info": {
            "name": "Legal Metrology Compliance Enforcement API — SIH 2026",
            "_postman_id": "legal-metrology-sih-2026-api",
            "description": "Comprehensive REST API suite for Indian Packaged Commodity Legal Metrology Compliance Enforcement under LM PCR 2011 & LM Act 2009.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {
                "name": "1. Authentication & RBAC",
                "item": [
                    {
                        "name": "Inspector Login (JSON)",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({"email": "inspector.mumbai@legalmetrology.gov.in", "password": "InspectorPassword@123"}, indent=2)
                            },
                            "url": {"raw": "{{baseUrl}}/api/v1/auth/login/json", "host": ["{{baseUrl}}"], "path": ["api", "v1", "auth", "login", "json"]}
                        }
                    },
                    {
                        "name": "Admin Login (JSON)",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({"email": "admin@legalmetrology.gov.in", "password": "AdminPassword@123"}, indent=2)
                            },
                            "url": {"raw": "{{baseUrl}}/api/v1/auth/login/json", "host": ["{{baseUrl}}"], "path": ["api", "v1", "auth", "login", "json"]}
                        }
                    },
                    {
                        "name": "Get Authenticated Officer Profile",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/auth/me", "host": ["{{baseUrl}}"], "path": ["api", "v1", "auth", "me"]}
                        }
                    }
                ]
            },
            {
                "name": "2. Statutory Rules & Gazette",
                "item": [
                    {
                        "name": "Get Active Rule Version",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/rules/version/active", "host": ["{{baseUrl}}"], "path": ["api", "v1", "rules", "version", "active"]}
                        }
                    },
                    {
                        "name": "List All Legal Metrology Rules",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/rules/", "host": ["{{baseUrl}}"], "path": ["api", "v1", "rules", ""]}
                        }
                    }
                ]
            },
            {
                "name": "3. Inspection & Pipeline Execution",
                "item": [
                    {
                        "name": "List Inspections (Paginated)",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/inspections/?skip=0&limit=20", "host": ["{{baseUrl}}"], "path": ["api", "v1", "inspections", ""], "query": [{"key": "skip", "value": "0"}, {"key": "limit", "value": "20"}]}
                        }
                    },
                    {
                        "name": "Run Dual OCR Consensus",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/inspections/{{inspectionId}}/ocr", "host": ["{{baseUrl}}"], "path": ["api", "v1", "inspections", "{{inspectionId}}", "ocr"]}
                        }
                    },
                    {
                        "name": "Extract Rule 6 Statutory Declarations",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/inspections/{{inspectionId}}/extract-declarations", "host": ["{{baseUrl}}"], "path": ["api", "v1", "inspections", "{{inspectionId}}", "extract-declarations"]}
                        }
                    },
                    {
                        "name": "Validate Statutory Compliance",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/inspections/{{inspectionId}}/validate", "host": ["{{baseUrl}}"], "path": ["api", "v1", "inspections", "{{inspectionId}}", "validate"]}
                        }
                    },
                    {
                        "name": "Generate Court-Admissible PDF Report",
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/inspections/{{inspectionId}}/report", "host": ["{{baseUrl}}"], "path": ["api", "v1", "inspections", "{{inspectionId}}", "report"]}
                        }
                    },
                    {
                        "name": "Public QR Verification Gateway",
                        "request": {
                            "method": "GET",
                            "url": {"raw": "{{baseUrl}}/api/v1/inspections/verify/{{qrToken}}", "host": ["{{baseUrl}}"], "path": ["api", "v1", "inspections", "verify", "{{qrToken}}"]}
                        }
                    }
                ]
            },
            {
                "name": "4. Executive Dashboard & Analytics",
                "item": [
                    {
                        "name": "Executive Dashboard KPIs",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/dashboard/metrics", "host": ["{{baseUrl}}"], "path": ["api", "v1", "dashboard", "metrics"]}
                        }
                    },
                    {
                        "name": "14-Day Compliance Velocity Trends",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/dashboard/trends?days=14", "host": ["{{baseUrl}}"], "path": ["api", "v1", "dashboard", "trends"], "query": [{"key": "days", "value": "14"}]}
                        }
                    },
                    {
                        "name": "Top Breached Statutory Rules",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/dashboard/top-violations?limit=5", "host": ["{{baseUrl}}"], "path": ["api", "v1", "dashboard", "top-violations"], "query": [{"key": "limit", "value": "5"}]}
                        }
                    },
                    {
                        "name": "GIS Jurisdiction Compliance Heatmap",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/dashboard/jurisdiction-heatmap", "host": ["{{baseUrl}}"], "path": ["api", "v1", "dashboard", "jurisdiction-heatmap"]}
                        }
                    },
                    {
                        "name": "Repeat Offender Recidivist Rankings",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/dashboard/repeat-offenders?limit=10", "host": ["{{baseUrl}}"], "path": ["api", "v1", "dashboard", "repeat-offenders"], "query": [{"key": "limit", "value": "10"}]}
                        }
                    }
                ]
            },
            {
                "name": "5. Audit Trail & Offline Sync",
                "item": [
                    {
                        "name": "Get Immutable Audit Logs (BSA 2023)",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwtToken}}"}],
                            "url": {"raw": "{{baseUrl}}/api/v1/audit-logs?skip=0&limit=25", "host": ["{{baseUrl}}"], "path": ["api", "v1", "audit-logs"], "query": [{"key": "skip", "value": "0"}, {"key": "limit", "value": "25"}]}
                        }
                    },
                    {
                        "name": "Batch Sync Offline Inspection Queue",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "Authorization", "value": "Bearer {{jwtToken}}"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "device_id": "TABLET-MH-01",
                                    "inspections": [
                                        {
                                            "client_offline_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                            "captured_at": "2026-08-25T17:00:00Z",
                                            "store_name": "Rural Mart",
                                            "district": "Ratnagiri",
                                            "state": "Maharashtra",
                                            "ocr_raw_text": "MRP Rs. 45.00 (incl. of all taxes)\nNET WT: 500 g\nMFD: 02/2026\nEXP: 12/2026\nMFG BY: Khed Mills Pvt Ltd, Ratnagiri 415612\nCONSUMER CARE: 1800-444-2222"
                                        }
                                    ]
                                }, indent=2)
                            },
                            "url": {"raw": "{{baseUrl}}/api/v1/inspections/batch-sync", "host": ["{{baseUrl}}"], "path": ["api", "v1", "inspections", "batch-sync"]}
                        }
                    }
                ]
            }
        ],
        "variable": [
            {"key": "baseUrl", "value": "http://localhost:8001"},
            {"key": "jwtToken", "value": "your_access_token_here"},
            {"key": "inspectionId", "value": "your_inspection_id_here"},
            {"key": "qrToken", "value": "your_qr_token_here"}
        ]
    }

    postman_path = os.path.join(docs_dir, "legal_metrology_api_postman_collection.json")
    with open(postman_path, "w", encoding="utf-8") as f:
        json.dump(postman_collection, f, indent=2)
    print(f"[OK] Exported Postman Collection v2.1: {postman_path}")

if __name__ == "__main__":
    export_specs()
