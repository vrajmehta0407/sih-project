import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { InspectionsListPage } from './pages/InspectionsListPage';
import { NewInspectionPage } from './pages/NewInspectionPage';
import { InspectionDetailPage } from './pages/InspectionDetailPage';
import { VerifyQRPage } from './pages/VerifyQRPage';
import { RulesPage } from './pages/RulesPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import PresentationPage from './pages/PresentationPage';
import InspectionMapPage from './pages/InspectionMapPage';
import CitizenPortalPage from './pages/CitizenPortalPage';
import BrandTrustSealPage from './pages/BrandTrustSealPage';
import PredictiveDispatchPage from './pages/PredictiveDispatchPage';
import CitizenBotSimulatorPage from './pages/CitizenBotSimulatorPage';
import ChallanSettlementPage from './pages/ChallanSettlementPage';
import RobustnessLabPage from './pages/RobustnessLabPage';
import RegulatoryCopilotPage from './pages/RegulatoryCopilotPage';
import EcommerceCrawlerPage from './pages/EcommerceCrawlerPage';
import LabTestingPage from './pages/LabTestingPage';
import CourtBriefPage from './pages/CourtBriefPage';
import DeceptivePackagingPage from './pages/DeceptivePackagingPage';
import GrandFinalePage from './pages/GrandFinalePage';
import PublicApisHubPage from './pages/PublicApisHubPage';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm font-semibold text-slate-600">Authenticating officer credentials...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function AppRoutes() {
  return (
    <Routes>
      {/* Screen 0: Public Marketing Landing Page with Cinematic Hero Video */}
      <Route path="/" element={<LandingPage />} />

      {/* Screen 1: Command Portal Login */}
      <Route path="/login" element={<LoginPage />} />

      {/* Publicly accessible standalone views */}
      <Route path="/verify/:qrToken" element={<VerifyQRPage />} />
      <Route path="/presentation" element={<PresentationPage />} />
      <Route path="/citizen-portal" element={<CitizenPortalPage />} />
      <Route path="/citizen-bot" element={<CitizenBotSimulatorPage />} />
      <Route path="/settle-challan" element={<ChallanSettlementPage />} />
      <Route path="/grand-finale-simulator" element={<GrandFinalePage />} />

      {/* Protected routes inside Layout */}
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/predictive-dispatch" element={<PredictiveDispatchPage />} />
        <Route path="/inspections" element={<InspectionsListPage />} />
        <Route path="/inspections/new" element={<NewInspectionPage />} />
        <Route path="/inspections/:id" element={<InspectionDetailPage />} />
        <Route path="/map" element={<InspectionMapPage />} />
        <Route path="/rules" element={<RulesPage />} />
        <Route path="/audit-logs" element={<AuditLogsPage />} />
        <Route path="/robustness-lab" element={<RobustnessLabPage />} />
        <Route path="/regulatory-copilot" element={<RegulatoryCopilotPage />} />
        <Route path="/ecommerce-crawler" element={<EcommerceCrawlerPage />} />
        <Route path="/lab-testing" element={<LabTestingPage />} />
        <Route path="/court-brief" element={<CourtBriefPage />} />
        <Route path="/deceptive-packaging" element={<DeceptivePackagingPage />} />
        <Route path="/brand-trust-seal" element={<BrandTrustSealPage />} />
        <Route path="/public-apis" element={<PublicApisHubPage />} />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
