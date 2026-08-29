import React, { useState, useEffect } from 'react';
import {
  Globe,
  Barcode,
  MapPin,
  DollarSign,
  CloudSun,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Search,
  ExternalLink,
  ShieldCheck,
  Zap,
  Info,
  Layers,
  Activity,
  Send,
  Building,
} from 'lucide-react';
import api from '../services/api';

export default function PublicApisHubPage() {
  const [activeTab, setActiveTab] = useState('barcode');
  const [apiStatus, setApiStatus] = useState(null);
  const [loadingStatus, setLoadingStatus] = useState(false);

  // Tab 1: Barcode / Open Food Facts State
  const [barcodeInput, setBarcodeInput] = useState('8901030865411');
  const [barcodeResult, setBarcodeResult] = useState(null);
  const [barcodeLoading, setBarcodeLoading] = useState(false);

  // Tab 2: India Post PIN Code State
  const [pincodeInput, setPincodeInput] = useState('110001');
  const [pincodeResult, setPincodeResult] = useState(null);
  const [pincodeLoading, setPincodeLoading] = useState(false);

  // Tab 3: Forex / Exchange Rate State
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  const [forexResult, setForexResult] = useState(null);
  const [forexLoading, setForexLoading] = useState(false);

  // Tab 4: Weather / Mandi Radar State
  const [selectedCity, setSelectedCity] = useState({ name: 'Mumbai, Maharashtra', lat: 19.0760, lon: 72.8777 });
  const [weatherResult, setWeatherResult] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);

  // Tab 5: Gemini AI Chat State
  const [aiPrompt, setAiPrompt] = useState('What are the penalties under Section 36(2) for a repeat offender who sells packaged food above the printed MRP?');
  const [aiResult, setAiResult] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

  const fetchApiStatus = async () => {
    setLoadingStatus(true);
    try {
      const res = await api.get('/public-apis/status');
      setApiStatus(res.data);
    } catch (err) {
      console.error('Failed to fetch public APIs status:', err);
    } finally {
      setLoadingStatus(false);
    }
  };

  useEffect(() => {
    fetchApiStatus();
    handleBarcodeLookup('8901030865411');
    handlePincodeLookup('110001');
    handleForexLookup('USD');
    handleWeatherLookup(19.0760, 72.8777);
  }, []);

  const handleBarcodeLookup = async (code = barcodeInput) => {
    if (!code) return;
    setBarcodeLoading(true);
    try {
      const res = await api.get(`/public-apis/barcode/${code}`);
      setBarcodeResult(res.data);
    } catch (err) {
      setBarcodeResult({ success: false, error: err.response?.data?.detail || err.message });
    } finally {
      setBarcodeLoading(false);
    }
  };

  const handlePincodeLookup = async (pin = pincodeInput) => {
    if (!pin) return;
    setPincodeLoading(true);
    try {
      const res = await api.get(`/public-apis/pincode/${pin}`);
      setPincodeResult(res.data);
    } catch (err) {
      setPincodeResult({ success: false, error: err.response?.data?.detail || err.message });
    } finally {
      setPincodeLoading(false);
    }
  };

  const handleForexLookup = async (curr = selectedCurrency) => {
    setForexLoading(true);
    try {
      const res = await api.get(`/public-apis/forex?base=${curr}`);
      setForexResult(res.data);
    } catch (err) {
      setForexResult({ success: false, error: err.response?.data?.detail || err.message });
    } finally {
      setForexLoading(false);
    }
  };

  const handleWeatherLookup = async (lat = selectedCity.lat, lon = selectedCity.lon) => {
    setWeatherLoading(true);
    try {
      const res = await api.get(`/public-apis/weather?lat=${lat}&lon=${lon}`);
      setWeatherResult(res.data);
    } catch (err) {
      setWeatherResult({ success: false, error: err.response?.data?.detail || err.message });
    } finally {
      setWeatherLoading(false);
    }
  };

  const handleAiChat = async () => {
    if (!aiPrompt.trim()) return;
    setAiLoading(true);
    try {
      const res = await api.post('/public-apis/ai-chat', { prompt: aiPrompt });
      setAiResult(res.data);
    } catch (err) {
      setAiResult({ success: false, error: err.response?.data?.detail || err.message });
    } finally {
      setAiLoading(false);
    }
  };

  const sampleBarcodes = [
    { label: 'Maggi 2-Minute Noodles (8901030865411)', code: '8901030865411' },
    { label: 'Tata Salt Vacuum Evaporated (8901063012345)', code: '8901063012345' },
    { label: 'Amul Butter 500g (8901262010059)', code: '8901262010059' },
    { label: 'Parle-G Glucose Biscuits (8901719101053)', code: '8901719101053' },
  ];

  const samplePincodes = [
    { label: '110001 — Connaught Place, New Delhi', pin: '110001' },
    { label: '400001 — Mumbai G.P.O., Fort, Maharashtra', pin: '400001' },
    { label: '560001 — MG Road, Bengaluru, Karnataka', pin: '560001' },
    { label: '249401 — Haridwar Industrial Area, Uttarakhand', pin: '249401' },
    { label: '700001 — Kolkata G.P.O., West Bengal', pin: '700001' },
  ];

  const indianCities = [
    { name: 'Mumbai, Maharashtra', lat: 19.0760, lon: 72.8777 },
    { name: 'New Delhi, NCR', lat: 28.6139, lon: 77.2090 },
    { name: 'Bengaluru, Karnataka', lat: 12.9716, lon: 77.5946 },
    { name: 'Kolkata, West Bengal', lat: 22.5726, lon: 88.3639 },
    { name: 'Ahmedabad, Gujarat', lat: 23.0225, lon: 72.5714 },
    { name: 'Haridwar / Roorkee, Uttarakhand', lat: 29.9457, lon: 78.1642 },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 sm:p-6 lg:p-8">
      {/* Header Banner */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="px-2.5 py-1 rounded bg-amber-500/20 text-amber-400 text-xs font-mono font-bold uppercase tracking-wider flex items-center gap-1.5 border border-amber-500/30">
                <Globe className="w-3.5 h-3.5" />
                Live External Integrations
              </span>
              <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 text-xs font-mono font-semibold flex items-center gap-1">
                <Activity className="w-3 h-3" />
                public-apis/public-apis Verified
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Public APIs & AI Intelligence Hub
            </h1>
            <p className="text-sm text-slate-400 mt-1 max-w-3xl">
              Live authoritative public APIs and AI/LLM keys powering the National Legal Metrology Compliance Enforcement Engine.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchApiStatus}
              disabled={loadingStatus}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium border border-slate-700 transition"
            >
              <RefreshCw className={`w-4 h-4 ${loadingStatus ? 'animate-spin text-amber-400' : ''}`} />
              Probe API Health
            </button>
            <a
              href="https://github.com/public-apis/public-apis"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-gradient-to-r from-amber-600 to-amber-500 text-white text-sm font-semibold hover:brightness-110 shadow-lg shadow-amber-500/10 transition"
            >
              <span>GitHub public-apis</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>

        {/* Global APIs Status Cards */}
        {apiStatus && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
            {apiStatus.public_apis.map((item, idx) => (
              <div key={idx} className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm hover:border-slate-700 transition">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-mono font-medium text-slate-400 truncate max-w-[150px]">
                    {item.category.split(' ')[0]}
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    <CheckCircle2 className="w-3 h-3" />
                    {item.status}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-white mb-1">{item.name}</h4>
                <p className="text-xs text-slate-400 line-clamp-2">{item.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
          {[
            { id: 'barcode', label: '1. Open Food Facts (Barcode)', icon: Barcode },
            { id: 'pincode', label: '2. India Post PIN Verifier', icon: MapPin },
            { id: 'forex', label: '3. Forex & Import Parity', icon: DollarSign },
            { id: 'weather', label: '4. Mandi Weather Radar', icon: CloudSun },
            { id: 'gemini', label: '5. Google Gemini AI Copilot', icon: Sparkles },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition ${
                  isActive
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-inner'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Interactive Tab Content */}
      <div className="max-w-7xl mx-auto">
        {/* ========================================================================= */}
        {/* TAB 1: OPEN FOOD FACTS BARCODE EXPLORER */}
        {/* ========================================================================= */}
        {activeTab === 'barcode' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md space-y-5">
              <div className="flex items-center gap-2 text-amber-400">
                <Barcode className="w-5 h-5" />
                <h3 className="text-base font-bold text-white">Live Commodity Barcode Lookup</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Connects to the <b>Open Food Facts Public API</b> to cross-verify physical label declarations against global commodity registries.
              </p>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Enter Barcode (EAN-13 / UPC):
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={barcodeInput}
                    onChange={(e) => setBarcodeInput(e.target.value)}
                    placeholder="e.g. 8901030865411"
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-amber-500 focus:outline-none"
                  />
                  <button
                    onClick={() => handleBarcodeLookup(barcodeInput)}
                    disabled={barcodeLoading}
                    className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-sm font-semibold flex items-center gap-1.5 transition"
                  >
                    <Search className={`w-4 h-4 ${barcodeLoading ? 'animate-spin' : ''}`} />
                    Query
                  </button>
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 mb-2 block">Quick Test Packaged Commodities:</span>
                <div className="space-y-1.5">
                  {sampleBarcodes.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setBarcodeInput(item.code);
                        handleBarcodeLookup(item.code);
                      }}
                      className="w-full text-left text-xs px-3 py-2 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800/80 text-slate-300 transition truncate"
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Results Panel */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md">
              <h3 className="text-base font-bold text-white mb-4 flex items-center justify-between">
                <span>Statutory Declarations Matrix (Open Food Facts Registry)</span>
                {barcodeResult?.success && (
                  <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    Verified Match
                  </span>
                )}
              </h3>

              {barcodeLoading ? (
                <div className="h-64 flex flex-col items-center justify-center space-y-3">
                  <div className="w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                  <p className="text-sm text-slate-400">Querying Open Food Facts database...</p>
                </div>
              ) : barcodeResult?.success ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-3">
                    <div>
                      <span className="text-[11px] text-slate-500 uppercase font-mono">Commodity Name</span>
                      <p className="text-sm font-bold text-white">{barcodeResult.product_name}</p>
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-500 uppercase font-mono">Brand Name</span>
                      <p className="text-sm font-semibold text-amber-400">{barcodeResult.brand}</p>
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-500 uppercase font-mono">Declared Net Quantity</span>
                      <p className="text-sm font-mono text-emerald-400">{barcodeResult.declared_quantity || 'Standard Single Item'}</p>
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-500 uppercase font-mono">Country of Origin</span>
                      <p className="text-sm text-slate-300">{barcodeResult.origin_country}</p>
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-500 uppercase font-mono">Packaging Type</span>
                      <p className="text-xs text-slate-400">{barcodeResult.packaging_type || 'Flexible pouch / Paper wrapper'}</p>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 flex flex-col items-center justify-center text-center">
                    {barcodeResult.image_url ? (
                      <img
                        src={barcodeResult.image_url}
                        alt="Product packaging"
                        className="max-h-44 object-contain rounded-lg border border-slate-800 shadow"
                      />
                    ) : (
                      <div className="w-32 h-32 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
                        <Barcode className="w-12 h-12" />
                      </div>
                    )}
                    <span className="text-xs text-slate-400 mt-3 font-mono">EAN Barcode: {barcodeResult.barcode}</span>
                    <span className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      Cross-referenced for Rule 6 compliance
                    </span>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-slate-400 bg-slate-950 rounded-lg border border-slate-800/80">
                  <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto mb-2" />
                  <p className="text-sm font-medium">{barcodeResult?.error || 'Enter a barcode to inspect declarations'}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: INDIA POST PIN CODE STATUTORY VERIFIER */}
        {/* ========================================================================= */}
        {activeTab === 'pincode' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md space-y-5">
              <div className="flex items-center gap-2 text-amber-400">
                <MapPin className="w-5 h-5" />
                <h3 className="text-base font-bold text-white">Rule 6(1)(a) PIN Code Audit</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Verifies that the manufacturer's postal PIN code extracted during OCR matches official <b>India Post</b> records.
              </p>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  6-Digit Postal PIN Code:
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    maxLength={6}
                    value={pincodeInput}
                    onChange={(e) => setPincodeInput(e.target.value)}
                    placeholder="e.g. 110001"
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-amber-500 focus:outline-none tracking-widest text-center font-bold"
                  />
                  <button
                    onClick={() => handlePincodeLookup(pincodeInput)}
                    disabled={pincodeLoading}
                    className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-sm font-semibold flex items-center gap-1.5 transition"
                  >
                    <Search className={`w-4 h-4 ${pincodeLoading ? 'animate-spin' : ''}`} />
                    Verify
                  </button>
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 mb-2 block">Sample Indian Manufacturing Hubs:</span>
                <div className="space-y-1.5">
                  {samplePincodes.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setPincodeInput(item.pin);
                        handlePincodeLookup(item.pin);
                      }}
                      className="w-full text-left text-xs px-3 py-2 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800/80 text-slate-300 transition"
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Results Panel */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md">
              <h3 className="text-base font-bold text-white mb-4 flex items-center justify-between">
                <span>India Post Official Directory Lookup</span>
                {pincodeResult?.is_valid && (
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold">
                    ✓ Valid Indian Postal Area
                  </span>
                )}
              </h3>

              {pincodeLoading ? (
                <div className="h-64 flex flex-col items-center justify-center space-y-3">
                  <div className="w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                  <p className="text-sm text-slate-400">Verifying with India Post open gateway...</p>
                </div>
              ) : pincodeResult?.is_valid ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
                      <span className="text-[11px] text-slate-500 uppercase font-mono">District</span>
                      <p className="text-base font-bold text-white mt-0.5">{pincodeResult.district}</p>
                    </div>
                    <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
                      <span className="text-[11px] text-slate-500 uppercase font-mono">State</span>
                      <p className="text-base font-bold text-amber-400 mt-0.5">{pincodeResult.state}</p>
                    </div>
                    <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
                      <span className="text-[11px] text-slate-500 uppercase font-mono">Postal Circle</span>
                      <p className="text-base font-bold text-slate-300 mt-0.5">{pincodeResult.circle || 'National'}</p>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                    <span className="text-xs font-semibold text-slate-300 block mb-2">
                      Delivery Post Offices in Postal Circle ({pincodeResult.total_post_offices} total):
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {pincodeResult.post_offices?.map((po, i) => (
                        <div key={i} className="bg-slate-900/80 p-2.5 rounded border border-slate-800 text-xs">
                          <div className="font-semibold text-white">{po.name}</div>
                          <div className="text-[11px] text-slate-400 flex justify-between mt-1">
                            <span>{po.branch_type}</span>
                            <span className="text-emerald-400">{po.delivery_status}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-slate-400 bg-slate-950 rounded-lg border border-slate-800/80">
                  <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto mb-2" />
                  <p className="text-sm font-medium">{pincodeResult?.error || 'Enter a PIN code to check compliance'}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: FOREX & IMPORT PARITY */}
        {/* ========================================================================= */}
        {activeTab === 'forex' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md space-y-5">
              <div className="flex items-center gap-2 text-amber-400">
                <DollarSign className="w-5 h-5" />
                <h3 className="text-base font-bold text-white">Imported Goods Currency Audit</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Live exchange rates from <b>ExchangeRate-API / Frankfurter</b> to audit Rule 6(1)(d) imported commodities and customs conversion declarations.
              </p>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Select Foreign Currency:
                </label>
                <select
                  value={selectedCurrency}
                  onChange={(e) => {
                    setSelectedCurrency(e.target.value);
                    handleForexLookup(e.target.value);
                  }}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2.5 text-sm text-white font-medium focus:border-amber-500 focus:outline-none"
                >
                  <option value="USD">USD — United States Dollar</option>
                  <option value="EUR">EUR — Euro</option>
                  <option value="GBP">GBP — British Pound</option>
                  <option value="AED">AED — UAE Dirham</option>
                  <option value="CNY">CNY — Chinese Yuan</option>
                  <option value="JPY">JPY — Japanese Yen</option>
                </select>
              </div>

              <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                <span className="text-xs text-slate-400 font-semibold block mb-1">Rule 6(1)(d) Statutory Requirement:</span>
                <p className="text-[11px] text-slate-300 leading-relaxed">
                  All imported pre-packaged commodities sold in India MUST declare the Maximum Retail Price in <b>Indian Rupees (₹/INR)</b> inclusive of all taxes.
                </p>
              </div>
            </div>

            {/* Results Panel */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md">
              <h3 className="text-base font-bold text-white mb-4">
                Real-Time Forex Conversion Matrix (1 {selectedCurrency} → INR)
              </h3>

              {forexLoading ? (
                <div className="h-64 flex flex-col items-center justify-center space-y-3">
                  <div className="w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                  <p className="text-sm text-slate-400">Fetching live forex market rates...</p>
                </div>
              ) : forexResult?.success ? (
                <div className="space-y-4">
                  <div className="bg-gradient-to-r from-amber-950/40 via-slate-900 to-slate-900 p-5 rounded-xl border border-amber-500/30">
                    <span className="text-xs font-mono text-amber-400 uppercase font-semibold">Official Spot Rate</span>
                    <div className="text-3xl font-extrabold text-white mt-1">
                      1 {selectedCurrency} = <span className="text-emerald-400">₹{forexResult.inr_exchange_rate}</span> INR
                    </div>
                    <span className="text-[11px] text-slate-400 mt-2 block">
                      Last Updated: {forexResult.last_updated || 'Live Public Feed'}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {forexResult.rates && Object.entries(forexResult.rates).map(([curr, rate], i) => (
                      <div key={i} className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                        <span className="text-[11px] text-slate-500 font-mono font-bold">{curr}</span>
                        <p className="text-sm font-bold text-slate-200 mt-0.5">{typeof rate === 'number' ? rate.toFixed(3) : rate}</p>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-slate-400 bg-slate-950 rounded-lg border border-slate-800/80">
                  <p className="text-sm font-medium">{forexResult?.error || 'Forex data unavailable'}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 4: MANDI WEATHER RADAR */}
        {/* ========================================================================= */}
        {activeTab === 'weather' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md space-y-5">
              <div className="flex items-center gap-2 text-amber-400">
                <CloudSun className="w-5 h-5" />
                <h3 className="text-base font-bold text-white">Field Inspection Weather Radar</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Connects to <b>Open-Meteo Public API</b> to assist enforcement directors in scheduling field raids and market inspections.
              </p>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Select Enforcement Region:
                </label>
                <div className="space-y-1.5">
                  {indianCities.map((city, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setSelectedCity(city);
                        handleWeatherLookup(city.lat, city.lon);
                      }}
                      className={`w-full text-left text-xs px-3 py-2.5 rounded-lg border transition ${
                        selectedCity.name === city.name
                          ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 font-semibold'
                          : 'bg-slate-950 hover:bg-slate-800 text-slate-300 border-slate-800'
                      }`}
                    >
                      {city.name}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Results Panel */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md">
              <h3 className="text-base font-bold text-white mb-4">
                Field Conditions & Raid Feasibility Index — {selectedCity.name}
              </h3>

              {weatherLoading ? (
                <div className="h-64 flex flex-col items-center justify-center space-y-3">
                  <div className="w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                  <p className="text-sm text-slate-400">Fetching Open-Meteo meteorological feed...</p>
                </div>
              ) : weatherResult?.success ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                      <span className="text-xs text-slate-500 font-mono">Current Temperature</span>
                      <div className="text-3xl font-extrabold text-amber-400 mt-1">
                        {weatherResult.temperature_celsius}°C
                      </div>
                    </div>
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                      <span className="text-xs text-slate-500 font-mono">Surface Wind Speed</span>
                      <div className="text-3xl font-extrabold text-sky-400 mt-1">
                        {weatherResult.windspeed_kmh} <span className="text-sm">km/h</span>
                      </div>
                    </div>
                    <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-center">
                      <span className="text-xs text-slate-500 font-mono">Raid Feasibility</span>
                      <div className="text-lg font-bold text-emerald-400 mt-2 flex items-center justify-center gap-1">
                        <CheckCircle2 className="w-4 h-4" />
                        {weatherResult.is_favorable_for_raid ? 'FAVORABLE' : 'ADVERSE'}
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <span className="text-xs text-slate-400 font-semibold uppercase font-mono block mb-1">
                      Enforcement Dispatch Advisory
                    </span>
                    <p className="text-sm text-slate-200">{weatherResult.field_advisory}</p>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-slate-400 bg-slate-950 rounded-lg border border-slate-800/80">
                  <p className="text-sm font-medium">{weatherResult?.error || 'Weather data unavailable'}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 5: GOOGLE GEMINI AI COPILOT */}
        {/* ========================================================================= */}
        {activeTab === 'gemini' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md space-y-5">
              <div className="flex items-center gap-2 text-amber-400">
                <Sparkles className="w-5 h-5" />
                <h3 className="text-base font-bold text-white">Gemini AI Legal Metrology Engine</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Direct integration with Google Gemini 1.5/2.0 Flash API for statutory legal reasoning and penalty calculations.
              </p>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                  Ask Legal Metrology Question:
                </label>
                <textarea
                  rows={4}
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  placeholder="Ask any statutory question on Legal Metrology..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-white focus:border-amber-500 focus:outline-none resize-none"
                />
                <button
                  onClick={handleAiChat}
                  disabled={aiLoading}
                  className="w-full mt-2.5 py-2.5 bg-gradient-to-r from-amber-600 to-amber-500 hover:brightness-110 text-white rounded-lg text-sm font-bold flex items-center justify-center gap-2 shadow-lg transition"
                >
                  <Send className={`w-4 h-4 ${aiLoading ? 'animate-spin' : ''}`} />
                  Generate AI Analysis
                </button>
              </div>

              <div>
                <span className="text-xs font-semibold text-slate-400 mb-2 block">Sample Legal Scenarios:</span>
                <div className="space-y-1.5">
                  {[
                    "What are the digital display requirements for e-commerce under Rule 6(10)?",
                    "Is font height below 1.0mm punishable under Section 36(1)?",
                    "Can retail overcharging be compounded under Section 48 without court filing?",
                  ].map((q, idx) => (
                    <button
                      key={idx}
                      onClick={() => setAiPrompt(q)}
                      className="w-full text-left text-xs px-3 py-2 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800/80 text-slate-300 transition truncate"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Results Panel */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-md">
              <h3 className="text-base font-bold text-white mb-4 flex items-center justify-between">
                <span>Gemini Generative Statutory Analysis</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold">
                  Google Gemini 1.5 Flash
                </span>
              </h3>

              {aiLoading ? (
                <div className="h-64 flex flex-col items-center justify-center space-y-3">
                  <div className="w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                  <p className="text-sm text-slate-400">Synthesizing statutory response with Gemini AI...</p>
                </div>
              ) : aiResult ? (
                <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-4">
                  {aiResult.configured ? (
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <Sparkles className="w-4 h-4 text-amber-400" />
                        <span className="text-xs font-mono text-emerald-400 font-semibold">
                          Live LLM Response ({aiResult.model})
                        </span>
                      </div>
                      <div className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">
                        {aiResult.response_text || aiResult.legal_opinion || 'No text returned.'}
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2 text-amber-400">
                        <Info className="w-5 h-5" />
                        <span className="text-sm font-bold">Standard Deterministic Engine Active</span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">
                        {aiResult.error || "Provide a GEMINI_API_KEY in backend/.env to activate live Google Gemini reasoning."}
                      </p>
                      {aiResult.response_text && (
                        <div className="p-3 bg-slate-900 rounded border border-slate-800 text-xs text-slate-300 whitespace-pre-wrap">
                          {aiResult.response_text}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-8 text-center text-slate-400 bg-slate-950 rounded-lg border border-slate-800/80">
                  <Sparkles className="w-8 h-8 text-amber-400 mx-auto mb-2" />
                  <p className="text-sm font-medium">Click "Generate AI Analysis" to query Gemini AI</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
