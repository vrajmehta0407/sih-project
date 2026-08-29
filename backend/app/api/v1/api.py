from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    rules,
    health,
    inspections,
    dashboard,
    audit,
    ecommerce,
    websockets,
    registry,
    citizen,
    copilot,
    lab_testing,
    court_brief,
    deceptive_packaging,
    grand_finale,
    public_apis,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["System Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & RBAC"])
api_router.include_router(users.router, prefix="/users", tags=["Inspectors & Users"])
api_router.include_router(rules.router, prefix="/rules", tags=["Legal Metrology Rules"])
api_router.include_router(inspections.router, prefix="/inspections", tags=["Inspections & Image Preprocessing"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Executive Analytics & Dashboard"])
api_router.include_router(audit.router, prefix="/audit-logs", tags=["Immutable Audit Trail"])
api_router.include_router(ecommerce.router, prefix="/ecommerce", tags=["E-Commerce Rule 6(10) Compliance Auditor"])
api_router.include_router(websockets.router, prefix="/ws", tags=["Real-Time WebSocket Stream"])
api_router.include_router(registry.router, prefix="/registry", tags=["National Product Reference Registry"])
api_router.include_router(citizen.router, prefix="/citizen", tags=["Citizen Grievance & Public Gateway"])
api_router.include_router(copilot.router, prefix="/copilot", tags=["AI Regulatory Copilot & Statutory Chat"])
api_router.include_router(lab_testing.router, prefix="/lab-testing", tags=["Central Laboratory Sample Verification & Gravimetric Tare"])
api_router.include_router(court_brief.router, prefix="/court-brief", tags=["Pre-Trial Court Evidence Brief & Sec 65B Certificate"])
api_router.include_router(deceptive_packaging.router, prefix="/deceptive-packaging", tags=["AI Deceptive Packaging & Volumetric Slack-Fill"])
api_router.include_router(grand_finale.router, prefix="/grand-finale", tags=["SIH 2026 Grand Finale Demo Simulator"])
api_router.include_router(public_apis.router, prefix="/public-apis", tags=["Public APIs & AI Integration Hub (public-apis)"])
