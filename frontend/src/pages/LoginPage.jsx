import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import {
  Scale,
  Lock,
  Mail,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  Eye,
  EyeOff,
  Sparkles,
  Users,
  Compass,
  CheckCircle2,
  Scan,
} from 'lucide-react';
import { GlassCard, WelcomeInterstitial } from '../design-system';

export const LoginPage = () => {
  const [searchParams] = useSearchParams();
  const initialRole = searchParams.get('role') || 'inspector';

  const [selectedRole, setSelectedRole] = useState(initialRole);
  const [email, setEmail] = useState('inspector.mumbai@legalmetrology.gov.in');
  const [password, setPassword] = useState('InspectorPassword@123');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);
  const [loggedInUser, setLoggedInUser] = useState(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const rolePresets = {
    inspector: {
      title: 'Field Inspector',
      email: 'inspector.mumbai@legalmetrology.gov.in',
      password: 'InspectorPassword@123',
      badge: 'On-Ground Enforcement',
      color: 'blue',
      icon: Scan,
    },
    supervisor: {
      title: 'Zonal Controller',
      email: 'supervisor.west@legalmetrology.gov.in',
      password: 'SupervisorPassword@123',
      badge: 'Zonal Adjudication',
      color: 'violet',
      icon: Scale,
    },
    director: {
      title: 'Enforcement Director',
      email: 'admin@legalmetrology.gov.in',
      password: 'AdminPassword@123',
      badge: 'National Strategy',
      color: 'amber',
      icon: Compass,
    },
  };

  const handleRoleSelect = (roleKey) => {
    setSelectedRole(roleKey);
    const preset = rolePresets[roleKey] || rolePresets.inspector;
    setError('');

    // Typewriter fill simulation
    let currentEmail = '';
    let currentPass = '';
    const targetEmail = preset.email;
    const targetPass = preset.password;

    setEmail('');
    setPassword('');

    let i = 0;
    const interval = setInterval(() => {
      if (i < targetEmail.length) {
        currentEmail += targetEmail[i];
        setEmail(currentEmail);
      }
      if (i < targetPass.length) {
        currentPass += targetPass[i];
        setPassword(currentPass);
      }
      i++;
      if (i >= Math.max(targetEmail.length, targetPass.length)) {
        clearInterval(interval);
      }
    }, 18);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const userProfile = await login(email, password);
      setIsSuccess(true);
      setLoggedInUser(userProfile);
      setTimeout(() => {
        setShowWelcome(true);
      }, 700);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          'Invalid officer credentials. Please verify your statutory SSO badge.'
      );
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center relative overflow-hidden selection:bg-blue-500 selection:text-white">
      {/* Post-Login Welcome Interstitial (Section 3.10) */}
      {showWelcome && (
        <WelcomeInterstitial
          user={loggedInUser}
          onComplete={() => navigate('/dashboard')}
        />
      )}

      {/* Decorative Background Elements */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-400/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header Bar */}
      <div className="max-w-6xl mx-auto w-full px-4 py-6 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-tr from-blue-600 to-purple-600 text-white shadow-tinted-blue group-hover:scale-105 transition-transform">
            <Scale className="h-5 w-5" />
          </div>
          <div>
            <span className="text-sm font-extrabold font-display tracking-tight text-slate-900 block leading-tight">
              LEGAL METROLOGY DIVISION
            </span>
            <span className="text-[10px] font-semibold text-primary-600 tracking-wider uppercase block">
              Ministry of Consumer Affairs · Govt. of India
            </span>
          </div>
        </Link>

        <Link
          to="/"
          className="text-xs font-semibold text-slate-500 hover:text-primary-600 transition-colors"
        >
          ← Back to Landing Page
        </Link>
      </div>

      {/* Main Split-Screen Container */}
      <div className="max-w-6xl mx-auto w-full px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Left Side: Ambient Brand & Statutory Overview */}
        <div className="lg:col-span-5 space-y-6">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-blue-50 border border-blue-200 text-xs font-semibold text-blue-700">
            <Sparkles className="h-3.5 w-3.5 text-blue-600" />
            <span>Statutory Verification Portal</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-extrabold font-display text-slate-900 tracking-tight leading-tight">
            Authenticate for{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Enforcement Access
            </span>
          </h1>

          <p className="text-sm text-slate-600 leading-relaxed">
            Secure regulatory gateway for authorized Legal Metrology Officers. Access AI-powered label audits, forensic ELA tamper inspection, and court-admissible dossiers.
          </p>

          {/* Statutory Badges List */}
          <div className="space-y-3 pt-2">
            <div className="flex items-center space-x-3 p-3 rounded-2xl bg-white border border-slate-100 shadow-soft">
              <div className="h-8 w-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs">
                §18
              </div>
              <div>
                <p className="text-xs font-bold text-slate-800">Legal Metrology Act, 2009</p>
                <p className="text-[11px] text-slate-500">Packaged Commodities Compliance</p>
              </div>
            </div>

            <div className="flex items-center space-x-3 p-3 rounded-2xl bg-white border border-slate-100 shadow-soft">
              <div className="h-8 w-8 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold text-xs">
                §63
              </div>
              <div>
                <p className="text-xs font-bold text-slate-800">BSA 2023 Digital Evidence</p>
                <p className="text-[11px] text-slate-500">SHA-256 Tamper-Proof Chain of Custody</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Reimagined Interactive Login Card */}
        <div className="lg:col-span-7">
          <GlassCard variant="default" className="p-8 sm:p-10 max-w-xl mx-auto">
            {/* Quick 1-Click Role Presets */}
            <div className="mb-6">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5">
                Select Pre-Configured Officer Role
              </label>
              <div className="grid grid-cols-3 gap-2.5">
                {Object.entries(rolePresets).map(([key, item]) => {
                  const Icon = item.icon;
                  const isActive = selectedRole === key;
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => handleRoleSelect(key)}
                      className={`p-3 rounded-2xl border text-left transition-all duration-200 ${
                        isActive
                          ? 'border-primary-500 bg-primary-50/60 ring-2 ring-primary-400/30 shadow-sm'
                          : 'border-slate-100 bg-slate-50/60 hover:bg-white hover:border-slate-200'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <Icon
                          className={`h-4 w-4 ${
                            isActive ? 'text-primary-600' : 'text-slate-500'
                          }`}
                        />
                        {isActive && (
                          <span className="h-2 w-2 rounded-full bg-primary-600" />
                        )}
                      </div>
                      <p className="text-xs font-bold text-slate-900 truncate">
                        {item.title}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Error Message with Shake Animation */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0, x: [0, -4, 4, -4, 4, 0] }}
                  exit={{ opacity: 0, y: -8 }}
                  className="mb-5 p-3.5 rounded-2xl bg-rose-50 border border-rose-200 flex items-center space-x-3 text-rose-700 text-xs font-semibold"
                >
                  <ShieldAlert className="h-4 w-4 shrink-0 text-rose-600" />
                  <span>{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Login Form */}
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Officer Official Email / SSO Identity
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Mail className="h-4 w-4" />
                  </div>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-10 pr-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500 transition-all"
                    placeholder="officer@legalmetrology.gov.in"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Statutory Access Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Lock className="h-4 w-4" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-10 pr-11 py-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500 transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading || isSuccess}
                  className="w-full relative flex items-center justify-center space-x-2 py-3.5 px-6 rounded-2xl text-sm font-bold text-white bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:opacity-95 shadow-tinted-blue transition-all disabled:opacity-75"
                >
                  {isSuccess ? (
                    <motion.div
                      initial={{ scale: 0.5, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="flex items-center space-x-2"
                    >
                      <CheckCircle2 className="h-5 w-5" />
                      <span>Identity Verified · Loading Portal</span>
                    </motion.div>
                  ) : loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Authenticating Credentials...</span>
                    </div>
                  ) : (
                    <>
                      <ShieldCheck className="h-4 w-4" />
                      <span>Authenticate & Launch Command Center</span>
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>
              </div>
            </form>

            <div className="mt-6 pt-5 border-t border-slate-100 text-center">
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Authorized Government Personnel Only · All Authentication Events Logged Under Sec 65B Evidence Act / BSA 2023
              </p>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};
export default LoginPage;
