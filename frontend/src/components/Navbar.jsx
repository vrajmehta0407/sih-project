import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Scale,
  LayoutDashboard,
  ClipboardList,
  PlusCircle,
  BookOpen,
  History,
  LogOut,
  MapPin,
  Megaphone,
  Award,
  Radar,
  MessageSquare,
  CreditCard,
  Sliders,
  Cpu,
  Globe,
  FlaskConical,
  Gavel,
  Box,
  Trophy,
  ChevronDown,
  Menu,
  X,
  Sparkles,
} from 'lucide-react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [labsDropdownOpen, setLabsDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const primaryNav = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/inspections', label: 'Inspections', icon: ClipboardList },
    { to: '/predictive-dispatch', label: 'AI Dispatch', icon: Radar },
    { to: '/map', label: 'GIS Heatmap', icon: MapPin },
  ];

  const labLinks = [
    { to: '/regulatory-copilot', label: 'AI Copilot', icon: Cpu },
    { to: '/ecommerce-crawler', label: 'E-Com Crawler', icon: Globe },
    { to: '/deceptive-packaging', label: 'Slack-Fill Lab', icon: Box },
    { to: '/lab-testing', label: 'NABL Testing Hub', icon: FlaskConical },
    { to: '/court-brief', label: 'Court Brief Generator', icon: Gavel },
    { to: '/brand-trust-seal', label: 'Brand Trust Scorecard', icon: Award },
    { to: '/settle-challan', label: 'e-Challan Gateway', icon: CreditCard },
    { to: '/robustness-lab', label: 'Robustness Lab', icon: Sliders },
    { to: '/citizen-portal', label: 'Citizen Portal', icon: Megaphone },
    { to: '/citizen-bot', label: 'WhatsApp Bot Simulator', icon: MessageSquare },
    { to: '/rules', label: 'Rules & Gazette', icon: BookOpen },
    { to: '/public-apis', label: 'Public APIs Hub', icon: Globe },
    { to: '/audit-logs', label: 'Audit Trail', icon: History },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-xl border-b border-slate-200/80 shadow-soft">
      {/* Top Government Strip */}
      <div className="bg-slate-900 px-4 py-1.5 text-[11px] text-slate-300 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="font-semibold text-white">Government of India</span>
          <span className="text-slate-400">· Ministry of Consumer Affairs · Legal Metrology Division</span>
        </div>
        <div className="hidden sm:flex items-center space-x-4 text-slate-400">
          <span>Active Rule: <b className="text-slate-200">LM-PCR-2011-V3</b></span>
          <span>BSA 2023 §63 Certified</span>
        </div>
      </div>

      {/* Main Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <div className="flex items-center space-x-8">
            <Link to="/dashboard" className="flex items-center space-x-3 group">
              <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-purple-600 to-pink-600 flex items-center justify-center text-white shadow-tinted-blue group-hover:scale-105 transition-transform">
                <Scale className="h-5 w-5" />
              </div>
              <div>
                <div className="font-extrabold font-display text-sm tracking-tight text-slate-900 flex items-center space-x-1.5">
                  <span>METROLOGY AI</span>
                  <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                    PORTAL
                  </span>
                </div>
                <div className="text-[10px] text-slate-500 font-medium">Compliance Command Center</div>
              </div>
            </Link>

            {/* Desktop Primary Links */}
            <nav className="hidden lg:flex items-center space-x-1">
              <Link
                to="/grand-finale-simulator"
                className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all flex items-center space-x-1.5 ${
                  location.pathname === '/grand-finale-simulator'
                    ? 'bg-amber-100 text-amber-900 border border-amber-300 shadow-sm'
                    : 'text-amber-700 bg-amber-50 hover:bg-amber-100/80 border border-amber-200'
                }`}
              >
                <Trophy className="h-3.5 w-3.5 text-amber-600" />
                <span>Grand Finale</span>
              </Link>

              {primaryNav.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.to;
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-colors flex items-center space-x-1.5 ${
                      isActive
                        ? 'bg-primary-50 text-primary-700 font-bold border border-primary-200 shadow-sm'
                        : 'text-slate-600 hover:text-primary-600 hover:bg-slate-50'
                    }`}
                  >
                    <Icon className="h-3.5 w-3.5" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}

              {/* Forensic Labs & Modules Dropdown */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setLabsDropdownOpen(!labsDropdownOpen)}
                  className="px-3.5 py-1.5 rounded-full text-xs font-semibold text-slate-600 hover:text-primary-600 hover:bg-slate-50 flex items-center space-x-1 transition-colors"
                >
                  <Sparkles className="h-3.5 w-3.5 text-purple-600" />
                  <span>Forensic Labs & Modules</span>
                  <ChevronDown className="h-3 w-3 ml-0.5" />
                </button>

                {labsDropdownOpen && (
                  <div
                    onMouseLeave={() => setLabsDropdownOpen(false)}
                    className="absolute top-full left-0 mt-2 w-72 rounded-3xl bg-white/95 backdrop-blur-xl border border-slate-200 p-2 shadow-soft-lg grid grid-cols-1 gap-1 z-50 animate-in fade-in slide-in-from-top-2 duration-150"
                  >
                    {labLinks.map((item) => {
                      const Icon = item.icon;
                      return (
                        <Link
                          key={item.to}
                          to={item.to}
                          onClick={() => setLabsDropdownOpen(false)}
                          className="flex items-center space-x-2.5 px-3 py-2 rounded-2xl text-xs font-medium text-slate-700 hover:bg-blue-50/70 hover:text-blue-700 transition-colors"
                        >
                          <div className="h-6 w-6 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600">
                            <Icon className="h-3.5 w-3.5" />
                          </div>
                          <span>{item.label}</span>
                        </Link>
                      );
                    })}
                  </div>
                )}
              </div>
            </nav>
          </div>

          {/* Right Action & Profile Area */}
          <div className="flex items-center space-x-3">
            {/* New Inspection Action Button */}
            <Link
              to="/inspections/new"
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:opacity-95 text-white text-xs font-bold px-4 py-2 rounded-full shadow-tinted-blue transition-transform hover:scale-105 active:scale-95"
            >
              <PlusCircle className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">New Inspection</span>
            </Link>

            {/* Officer Profile Badge */}
            {user ? (
              <div className="flex items-center space-x-3 pl-3 border-l border-slate-200">
                <div className="text-right hidden sm:block">
                  <p className="text-xs font-bold text-slate-800 leading-tight">
                    {user.full_name || user.email}
                  </p>
                  <p className="text-[10px] font-semibold text-primary-600">
                    {user.role === 'admin' ? 'DIRECTOR' : 'INSPECTOR'} · {user.jurisdiction_state || 'HQ'}
                  </p>
                </div>

                <button
                  onClick={handleLogout}
                  title="Sign Out"
                  className="h-8 w-8 rounded-full bg-slate-100 hover:bg-rose-50 hover:text-rose-600 text-slate-500 flex items-center justify-center transition-colors shadow-sm"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="text-xs font-bold px-4 py-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-800 transition-colors"
              >
                Officer Login
              </Link>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden h-9 w-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-slate-200 bg-white/95 backdrop-blur-xl px-4 pt-3 pb-6 space-y-2">
          <Link
            to="/grand-finale-simulator"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center space-x-2 px-3 py-2 rounded-xl text-xs font-bold bg-amber-50 text-amber-900 border border-amber-200"
          >
            <Trophy className="h-4 w-4 text-amber-600" />
            <span>🏆 Grand Finale Simulator</span>
          </Link>

          {primaryNav.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-slate-700 hover:bg-blue-50"
              >
                <Icon className="h-4 w-4 text-primary-600" />
                <span>{item.label}</span>
              </Link>
            );
          })}

          <div className="pt-2 border-t border-slate-100">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-3 mb-1">
              Forensic Labs
            </p>
            <div className="grid grid-cols-2 gap-1">
              {labLinks.slice(0, 8).map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className="px-3 py-1.5 rounded-lg text-[11px] font-medium text-slate-600 hover:bg-slate-50 truncate"
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
export default Navbar;
