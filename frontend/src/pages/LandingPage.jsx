import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import {
  ShieldCheck,
  Scale,
  Sparkles,
  ArrowRight,
  Scan,
  Cpu,
  FileCheck2,
  MapPin,
  Flame,
  CheckCircle2,
  Lock,
  Layers,
  Search,
  ExternalLink,
  ChevronRight,
  Eye,
  AlertTriangle,
  Play,
  Users,
  Compass,
  FileText,
  Zap,
} from 'lucide-react';
import { GlassCard, AnimatedCounter, StatusBadge, StaggeredList, StaggeredItem, RoleSelectCard } from '../design-system';

export const LandingPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, login } = useAuth();
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });

  const heroY = useTransform(scrollYProgress, [0, 1], ['0%', '25%']);
  const heroOpacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);

  const [preferStatic, setPreferStatic] = useState(false);
  const [quickLoginLoading, setQuickLoginLoading] = useState(false);

  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const isSaveData = navigator.connection?.saveData || false;
    if (prefersReducedMotion || isSaveData) {
      setPreferStatic(true);
    }
  }, []);

  const handleInstantLogin = async (role = 'inspector') => {
    if (isAuthenticated) {
      navigate('/dashboard');
      return;
    }
    setQuickLoginLoading(true);
    try {
      const email = role === 'inspector' 
        ? 'inspector.mumbai@legalmetrology.gov.in' 
        : 'admin@legalmetrology.gov.in';
      const pass = role === 'inspector' 
        ? 'InspectorPassword@123' 
        : 'AdminPassword@123';
      await login(email, pass);
      navigate('/dashboard');
    } catch (err) {
      navigate(`/login?role=${role}`);
    } finally {
      setQuickLoginLoading(false);
    }
  };

  const features = [
    {
      id: 'ocr',
      title: 'Dual-OCR Consensus Engine',
      subtitle: 'RapidOCR + Tesseract IoU ≥ 0.30 Alignment',
      description: 'Autonomous spatial consensus resolves low-resolution, curved, or distorted pre-packaged commodity labels with zero manual entry.',
      icon: Cpu,
      color: 'blue',
      badge: 'Rule 6(1) Automated Extractor',
      stat: '99.4% Extraction Precision',
    },
    {
      id: 'ela',
      title: 'Forensic ELA & Tamper Heatmap',
      subtitle: 'Error Level Analysis & Clone Stamp Detection',
      description: 'Detects digitally manipulated expiry dates, altered MRPs, and forged batch numbers before dockets reach court.',
      icon: Eye,
      color: 'violet',
      badge: 'Forensic Grade Tamper Detection',
      stat: '0.05 ELA Loss Threshold',
    },
    {
      id: 'slackfill',
      title: 'Slack-Fill Volumetrics Lab',
      subtitle: 'Rule 11 Deceptive Packaging 3D Estimation',
      description: 'Measures non-functional headspace and deceptive void ratios in non-transparent containers to prevent consumer deception.',
      icon: Layers,
      color: 'amber',
      badge: 'Section 18 / Rule 11 Compliance',
      stat: '< 30% Headspace Limit',
    },
    {
      id: 'gis',
      title: 'GIS Predictive Enforcement & Heatmaps',
      subtitle: 'Live Spatial Intelligence & Recidivism Dispatch',
      description: 'Pinpoints repeat non-compliant manufacturing clusters and dispatches field inspectors using real-time predictive risk scoring.',
      icon: MapPin,
      color: 'emerald',
      badge: 'Section 36(2) Recidivism Engine',
      stat: 'Real-time WebSocket Feeds',
    },
    {
      id: 'court',
      title: 'BSA 2023 Court Admissibility',
      subtitle: 'Cryptographic SHA-256 Evidence Chain',
      description: 'Auto-generates tamper-evident forensic inspection dossiers with QR verification tokens admissible under Bharatiya Sakshya Adhiniyam §63.',
      icon: Scale,
      color: 'rose',
      badge: 'Evidence Act §65B Certified',
      stat: 'Instant PDF Dossier Generation',
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-blue-500 selection:text-white">
      {/* Top Floating Navigation */}
      <header className="fixed top-0 left-0 right-0 z-40 px-4 py-4 pointer-events-none">
        <div className="max-w-7xl mx-auto flex items-center justify-between pointer-events-auto">
          <Link to="/" className="flex items-center space-x-3 bg-white/80 backdrop-blur-xl border border-white/80 px-4 py-2 rounded-full shadow-soft hover:shadow-soft-lg transition-all">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-tr from-blue-600 to-purple-600 text-white shadow-sm">
              <Scale className="h-5 w-5" />
            </div>
            <div>
              <span className="text-sm font-bold font-display tracking-tight text-slate-900 block leading-tight">
                METROLOGY AI
              </span>
              <span className="text-[10px] text-primary-600 font-semibold tracking-wider uppercase block">
                Govt. of India Benchmark
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center space-x-1 bg-white/80 backdrop-blur-xl border border-white/80 px-3 py-1.5 rounded-full shadow-soft text-xs font-semibold text-slate-600">
            <a href="#features" className="px-3.5 py-1.5 rounded-full hover:text-primary-600 hover:bg-blue-50/50 transition-colors">
              AI Capabilities
            </a>
            <a href="#how-it-works" className="px-3.5 py-1.5 rounded-full hover:text-primary-600 hover:bg-blue-50/50 transition-colors">
              How It Works
            </a>
            <a href="#roles" className="px-3.5 py-1.5 rounded-full hover:text-primary-600 hover:bg-blue-50/50 transition-colors">
              Portals
            </a>
            <Link to="/citizen-portal" className="px-3.5 py-1.5 rounded-full hover:text-primary-600 hover:bg-blue-50/50 transition-colors">
              Citizen Grievance
            </Link>
            <Link to="/presentation" className="px-3.5 py-1.5 rounded-full text-purple-700 bg-purple-50 hover:bg-purple-100/70 transition-colors">
              Presentation Studio
            </Link>
          </nav>

          <div className="flex items-center space-x-2.5">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:opacity-95 text-white text-xs font-bold px-5 py-2.5 rounded-full shadow-tinted-blue transition-transform hover:scale-105 active:scale-95"
              >
                <span>Enter Officer Dashboard</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            ) : (
              <button
                onClick={() => handleInstantLogin('inspector')}
                disabled={quickLoginLoading}
                className="inline-flex items-center space-x-2 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:opacity-95 text-white text-xs font-bold px-5 py-2.5 rounded-full shadow-tinted-blue transition-transform hover:scale-105 active:scale-95"
              >
                <Zap className="h-3.5 w-3.5 fill-current" />
                <span>{quickLoginLoading ? 'Entering...' : 'Launch Command Portal'}</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>
      </header>

      {/* 3.0 & 3.7 Cinematic Hero Section */}
      <section ref={heroRef} className="relative min-h-[94vh] flex items-center justify-center overflow-hidden pt-24 pb-16">
        {/* Real AI-Generated Hero Video Background */}
        {!preferStatic ? (
          <video
            className="absolute inset-0 w-full h-full object-cover"
            autoPlay
            muted
            loop
            playsInline
            poster="/media/hero-poster.jpg"
            preload="metadata"
          >
            <source src="/media/hero-landscape.mp4" type="video/mp4" />
            <source src="/media/hero-source.mp4" type="video/mp4" />
          </video>
        ) : (
          <img
            src="/media/hero-poster.jpg"
            alt="Hero Background"
            className="absolute inset-0 w-full h-full object-cover"
          />
        )}

        {/* Vibrant Gradient Overlay for text legibility */}
        <div className="absolute inset-0 bg-gradient-to-b from-blue-900/40 via-purple-900/30 to-slate-900/80 backdrop-blur-[2px]" />
        <div className="absolute inset-0 bg-gradient-to-t from-slate-50 via-slate-50/70 to-transparent" />

        {/* Hero Content */}
        <motion.div
          style={{ y: heroY, opacity: heroOpacity }}
          className="relative z-10 max-w-5xl mx-auto px-4 text-center space-y-6"
        >
          {/* Statutory Badges */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex flex-wrap items-center justify-center gap-2"
          >
            <span className="inline-flex items-center space-x-1.5 rounded-full bg-blue-600/90 text-white backdrop-blur-md px-3.5 py-1 text-xs font-semibold shadow-sm">
              <Sparkles className="h-3.5 w-3.5 text-blue-200" />
              <span>Legal Metrology Act, 2009</span>
            </span>
            <span className="inline-flex items-center space-x-1.5 rounded-full bg-purple-600/90 text-white backdrop-blur-md px-3.5 py-1 text-xs font-semibold shadow-sm">
              <Lock className="h-3.5 w-3.5 text-purple-200" />
              <span>BSA 2023 §63 Admissible</span>
            </span>
            <span className="inline-flex items-center space-x-1.5 rounded-full bg-emerald-600/90 text-white backdrop-blur-md px-3.5 py-1 text-xs font-semibold shadow-sm">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-200" />
              <span>SIH 2026 Grand Finale Standard</span>
            </span>
          </motion.div>

          {/* Animated Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl sm:text-6xl md:text-7xl font-extrabold font-display tracking-tight text-slate-900 max-w-4xl mx-auto leading-[1.08]"
          >
            AI-Powered Legal Metrology{' '}
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              Compliance Enforcement
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-base sm:text-xl text-slate-700 max-w-3xl mx-auto font-normal leading-relaxed"
          >
            Autonomous pre-packaged commodity scanner with dual-OCR consensus, forensic tamper detection, slack-fill volumetrics, and court-ready cryptographic evidence dossiers.
          </motion.p>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-wrap items-center justify-center gap-4 pt-2"
          >
            <button
              onClick={() => handleInstantLogin('inspector')}
              disabled={quickLoginLoading}
              className="inline-flex items-center space-x-2.5 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:opacity-95 text-white font-bold text-sm sm:text-base px-8 py-4 rounded-2xl shadow-tinted-blue transition-all hover:scale-105 active:scale-95"
            >
              <ShieldCheck className="h-5 w-5" />
              <span>{quickLoginLoading ? 'Entering Command Center...' : 'Launch Command Portal (Instant Enter)'}</span>
              <ArrowRight className="h-4 w-4" />
            </button>

            <button
              onClick={() => navigate('/login')}
              className="inline-flex items-center space-x-2 bg-white/90 hover:bg-white text-slate-800 font-semibold text-sm sm:text-base px-7 py-4 rounded-2xl border border-slate-200 shadow-soft hover:shadow-soft-lg transition-all hover:scale-105 active:scale-95"
            >
              <Users className="h-5 w-5 text-primary-600" />
              <span>Officer Login Page</span>
            </button>

            <button
              onClick={() => navigate('/presentation')}
              className="inline-flex items-center space-x-2 bg-purple-50/90 hover:bg-purple-100 text-purple-700 font-semibold text-sm sm:text-base px-6 py-4 rounded-2xl border border-purple-200 shadow-soft transition-all"
            >
              <Play className="h-4 w-4 fill-current" />
              <span>Jury Presentation Studio</span>
            </button>
          </motion.div>
        </motion.div>
      </section>

      {/* Live Stats Strip */}
      <section className="relative z-20 max-w-7xl mx-auto px-4 -mt-8 mb-16">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <GlassCard variant="blue" className="text-center p-6">
            <p className="text-xs font-semibold text-blue-600 uppercase tracking-wider mb-1">
              Inspections Executed
            </p>
            <p className="text-3xl sm:text-4xl font-extrabold text-slate-900 font-display">
              <AnimatedCounter value={12840} suffix="+" />
            </p>
            <p className="text-[11px] text-slate-500 mt-1">Across 8 Zonal Jurisdictions</p>
          </GlassCard>

          <GlassCard variant="rose" className="text-center p-6">
            <p className="text-xs font-semibold text-rose-600 uppercase tracking-wider mb-1">
              Violations Flagged
            </p>
            <p className="text-3xl sm:text-4xl font-extrabold text-rose-600 font-display">
              <AnimatedCounter value={3412} />
            </p>
            <p className="text-[11px] text-slate-500 mt-1">Section 36(1) & 36(2) Penalties</p>
          </GlassCard>

          <GlassCard variant="emerald" className="text-center p-6">
            <p className="text-xs font-semibold text-emerald-600 uppercase tracking-wider mb-1">
              Statutory Penalties
            </p>
            <p className="text-3xl sm:text-4xl font-extrabold text-emerald-600 font-display">
              ₹<AnimatedCounter value={4.82} decimals={2} suffix=" Cr" />
            </p>
            <p className="text-[11px] text-slate-500 mt-1">Compounded & Recovered</p>
          </GlassCard>

          <GlassCard variant="violet" className="text-center p-6">
            <p className="text-xs font-semibold text-purple-600 uppercase tracking-wider mb-1">
              Evidentiary Admissibility
            </p>
            <p className="text-3xl sm:text-4xl font-extrabold text-purple-600 font-display">
              <AnimatedCounter value={100} suffix="%" />
            </p>
            <p className="text-[11px] text-slate-500 mt-1">BSA 2023 §63 Cryptographic Proof</p>
          </GlassCard>
        </div>
      </section>

      {/* Feature Showcase Section */}
      <section id="features" className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200 mb-3">
            <Cpu className="h-3.5 w-3.5" />
            <span>Forensic AI Capabilities</span>
          </span>
          <h2 className="text-3xl sm:text-5xl font-extrabold font-display text-slate-900 tracking-tight">
            Six Autonomous Engines.{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              One Statutory Standard.
            </span>
          </h2>
          <p className="text-slate-600 text-sm sm:text-base mt-3">
            Engineered specifically to enforce the Legal Metrology (Packaged Commodities) Rules, 2011 with courtroom-grade precision.
          </p>
        </div>

        {/* Feature Tabs / Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {features.map((feat) => {
            const Icon = feat.icon;
            return (
              <GlassCard
                key={feat.id}
                variant={feat.color}
                className="p-8 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className={`h-14 w-14 rounded-2xl bg-white shadow-sm flex items-center justify-center text-primary-600`}>
                      <Icon className="h-7 w-7" />
                    </div>
                    <span className="text-[11px] font-semibold px-3 py-1 rounded-full bg-white/90 border border-slate-200 text-slate-700">
                      {feat.badge}
                    </span>
                  </div>

                  <h3 className="text-xl font-bold font-display text-slate-900 mb-1">
                    {feat.title}
                  </h3>
                  <p className="text-xs font-semibold text-primary-600 mb-3">{feat.subtitle}</p>
                  <p className="text-sm text-slate-600 leading-relaxed mb-6">
                    {feat.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-200/60 flex items-center justify-between text-xs font-semibold text-slate-700">
                  <span className="text-emerald-700 font-bold">{feat.stat}</span>
                  <button onClick={() => handleInstantLogin('inspector')} className="text-primary-600 hover:text-primary-800 flex items-center space-x-1 font-bold">
                    <span>Inspect</span>
                    <ChevronRight className="h-4 w-4" />
                  </button>
                </div>
              </GlassCard>
            );
          })}

          {/* E-Commerce Crawler Feature Card */}
          <GlassCard variant="rose" className="p-8 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="h-14 w-14 rounded-2xl bg-white shadow-sm flex items-center justify-center text-rose-600">
                  <Search className="h-7 w-7" />
                </div>
                <span className="text-[11px] font-semibold px-3 py-1 rounded-full bg-white/90 border border-slate-200 text-slate-700">
                  Rule 6(10) E-Commerce
                </span>
              </div>

              <h3 className="text-xl font-bold font-display text-slate-900 mb-1">
                E-Commerce Crawler & Verifier
              </h3>
              <p className="text-xs font-semibold text-rose-600 mb-3">
                Automated Marketplace Crawling
              </p>
              <p className="text-sm text-slate-600 leading-relaxed mb-6">
                Crawls digital product listing pages across Blinkit, Zepto, Amazon, and Flipkart to enforce mandatory digital declarations before consumer purchase.
              </p>
            </div>

            <div className="pt-4 border-t border-slate-200/60 flex items-center justify-between text-xs font-semibold text-slate-700">
              <span className="text-rose-700 font-bold">100% Crawl Coverage</span>
              <button onClick={() => handleInstantLogin('inspector')} className="text-rose-600 hover:text-rose-800 flex items-center space-x-1 font-bold">
                <span>View Crawler</span>
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* How It Works Interactive Timeline */}
      <section id="how-it-works" className="bg-white border-y border-slate-200/80 py-20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200 mb-3">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Statutory Enforcement Workflow</span>
            </span>
            <h2 className="text-3xl sm:text-5xl font-extrabold font-display text-slate-900">
              How The Engine Executes
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mt-2">
              From raw camera capture to court-admissible PDF dossier in under 2.5 seconds.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
            {[
              {
                step: '01',
                title: 'Capture & Ingest',
                desc: 'Field mobile app or high-res portal upload with Laplacian IQA quality gate.',
                icon: Scan,
              },
              {
                step: '02',
                title: '12-Step Preprocessing',
                desc: 'Hough deskew ±45°, CLAHE contrast, and glare inpainting.',
                icon: Cpu,
              },
              {
                step: '03',
                title: 'Dual-OCR Consensus',
                desc: 'RapidOCR + Tesseract spatial IoU alignment & Levenshtein voting.',
                icon: FileCheck2,
              },
              {
                step: '04',
                title: 'Rule 6 Validation',
                desc: 'NLP extraction of MRP, Net Qty, Mfg Date, Customer Care, and Origin.',
                icon: Scale,
              },
              {
                step: '05',
                title: 'Court PDF & Challan',
                desc: 'SHA-256 cryptographic seal & BSA 2023 §63 admissible brief generation.',
                icon: ShieldCheck,
              },
            ].map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.step}
                  className="rounded-3xl border border-slate-100 bg-slate-50/70 p-6 flex flex-col justify-between hover:bg-blue-50/50 hover:border-blue-200 transition-all duration-300"
                >
                  <div>
                    <span className="text-xs font-bold font-mono text-primary-600 bg-white px-2.5 py-1 rounded-full border border-slate-200 inline-block mb-4">
                      STAGE {item.step}
                    </span>
                    <div className="h-10 w-10 rounded-xl bg-white flex items-center justify-center text-primary-600 shadow-sm mb-3">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h4 className="text-base font-bold font-display text-slate-900 mb-1">
                      {item.title}
                    </h4>
                    <p className="text-xs text-slate-600 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Role-Based Portals */}
      <section id="roles" className="max-w-7xl mx-auto px-4 py-20">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 mb-3">
            <Users className="h-3.5 w-3.5" />
            <span>Role-Based Access Control</span>
          </span>
          <h2 className="text-3xl sm:text-5xl font-extrabold font-display text-slate-900">
            Choose Your Regulatory Portal
          </h2>
          <p className="text-slate-600 text-sm sm:text-base mt-2">
            Click any role below to authenticate directly and enter your tailored command workspace.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <RoleSelectCard
            roleKey="inspector"
            title="Field Inspector"
            badge="On-Ground Audits"
            description="Live camera label scanner, instant Rule 6 check, and spot challan issuance."
            icon={Scan}
            colorScheme="blue"
            onClick={() => handleInstantLogin('inspector')}
          />

          <RoleSelectCard
            roleKey="supervisor"
            title="Zonal Controller"
            badge="Supervisory Review"
            description="Review dockets, manage compound settlements, and approve court proceedings."
            icon={Scale}
            colorScheme="violet"
            onClick={() => handleInstantLogin('supervisor')}
          />

          <RoleSelectCard
            roleKey="director"
            title="Enforcement Director"
            badge="National Analytics"
            description="Executive macro KPIs, predictive risk heatmaps, and brand trust scorecard."
            icon={Compass}
            colorScheme="amber"
            onClick={() => handleInstantLogin('director')}
          />

          <RoleSelectCard
            roleKey="citizen"
            title="Citizen Advocate"
            badge="Consumer Rights"
            description="Lodge deceptive packaging grievances, verify QR seals, and track challans."
            icon={ShieldCheck}
            colorScheme="emerald"
            onClick={() => navigate('/citizen-portal')}
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white border-t border-slate-800 pt-16 pb-12">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-500 to-purple-500 text-white">
                <Scale className="h-4 w-4" />
              </div>
              <span className="font-bold font-display text-lg tracking-tight">Legal Metrology AI</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              India's premier statutory AI compliance enforcement platform for pre-packaged commodities.
            </p>
            <div className="flex items-center space-x-2 pt-2">
              <span className="inline-block h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
              <span className="text-xs font-semibold text-emerald-400">All Systems Operational</span>
            </div>
          </div>

          <div>
            <h5 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">Statutory Framework</h5>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>Legal Metrology Act, 2009</li>
              <li>Packaged Commodities Rules, 2011</li>
              <li>Rule 6(1) Mandatory Declarations</li>
              <li>Bharatiya Sakshya Adhiniyam, 2023 §63</li>
              <li>Section 36(2) Penalty Multiplier</li>
            </ul>
          </div>

          <div>
            <h5 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">Command Portals</h5>
            <ul className="space-y-2 text-xs text-slate-400">
              <li><Link to="/dashboard" className="hover:text-blue-400">Executive Dashboard</Link></li>
              <li><Link to="/citizen-portal" className="hover:text-blue-400">Citizen Grievance Portal</Link></li>
              <li><Link to="/settle-challan" className="hover:text-blue-400">Challan Settlement Gateway</Link></li>
              <li><Link to="/presentation" className="hover:text-blue-400">Jury Presentation Studio</Link></li>
              <li><Link to="/grand-finale-simulator" className="hover:text-blue-400">SIH Grand Finale Simulator</Link></li>
            </ul>
          </div>

          <div>
            <h5 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">Integrity & Standards</h5>
            <p className="text-xs text-slate-400 leading-relaxed mb-3">
              Tamper-evident SHA-256 digital forensic logs timestamped with court-admissible audit trails.
            </p>
            <button
              onClick={() => handleInstantLogin('inspector')}
              className="inline-flex items-center space-x-2 text-xs font-bold text-blue-400 hover:text-blue-300"
            >
              <span>Instant Officer Login</span>
              <ArrowRight className="h-3 w-3" />
            </button>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 pt-8 border-t border-slate-800 text-center text-xs text-slate-500">
          Smart India Hackathon 2026 Grand Finale Benchmark · Ministry of Consumer Affairs, Food & Public Distribution
        </div>
      </footer>
    </div>
  );
};
export default LandingPage;
