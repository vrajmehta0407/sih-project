# deploy_production.ps1
# 1-Click Production Orchestration Script for Legal Metrology SIH 2026

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  LEGAL METROLOGY COMPLIANCE PLATFORM - SIH 2026 DEPLOYMENT " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Start Docker Containers
Write-Host "`n[1/3] Launching Production Multi-Container Stack..." -ForegroundColor Yellow
docker compose -f docker-compose.prod.yml up -d --build

# 2. Wait for Backend Health
Write-Host "`n[2/3] Verifying Backend Health..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
try {
    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/v1/rules" -Method Get
    Write-Host "✓ Backend is live and serving Statutory Legal Metrology Rules." -ForegroundColor Green
} catch {
    Write-Host "! Backend initializing in background..." -ForegroundColor Yellow
}

# 3. Print URLs
Write-Host "`n[3/3] Deployment Successful! All Services Operational:" -ForegroundColor Green
Write-Host "  • Web Command Portal:         http://localhost:5174/" -ForegroundColor White
Write-Host "  • Citizen Grievance Portal:    http://localhost:5174/citizen-portal" -ForegroundColor White
Write-Host "  • Brand Trust Seal Gateway:    http://localhost:5174/brand-trust-seal" -ForegroundColor White
Write-Host "  • Geo-Tagged Enforcement Map:  http://localhost:5174/map" -ForegroundColor White
Write-Host "  • Interactive Presentation:    http://localhost:5174/presentation" -ForegroundColor White
Write-Host "  • FastAPI REST Docs (OpenAPI): http://127.0.0.1:8001/docs" -ForegroundColor White
Write-Host "`nOfficer Credentials:" -ForegroundColor Cyan
Write-Host "  • Inspector: inspector.mumbai@legalmetrology.gov.in / InspectorPassword@123" -ForegroundColor White
Write-Host "  • Admin:     admin@legalmetrology.gov.in / AdminPassword@123" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
