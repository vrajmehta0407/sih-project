import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import {
  Upload,
  Camera,
  CheckCircle,
  X,
  MapPin,
  Building2,
  FileText,
  AlertCircle,
  ArrowRight,
  Sparkles,
  Layers,
  Cpu,
} from 'lucide-react';
import { GlassCard, PipelineLoader } from '../design-system';

export const NewInspectionPage = () => {
  const navigate = useNavigate();
  const [district, setDistrict] = useState('Mumbai Suburban');
  const [state, setState] = useState('Maharashtra');
  const [storeName, setStoreName] = useState('Modern Supermarket & Retail');
  const [storeAddress, setStoreAddress] = useState('Shop 4, Linking Road, Bandra West, Mumbai 400050');
  const [gpsLat, setGpsLat] = useState('19.0596');
  const [gpsLon, setGpsLon] = useState('72.8295');
  const [inspectorNotes, setInspectorNotes] = useState('Routine market surveillance audit under Sec 18 LM Act 2009.');

  // Multi-side image uploads: { side: 'front'|'back'|'left'|'right'|'top', file, preview }
  const [sideUploads, setSideUploads] = useState({
    front: null,
    back: null,
    left: null,
    right: null,
    top: null,
  });

  const [loading, setLoading] = useState(false);
  const [showPipeline, setShowPipeline] = useState(false);
  const [error, setError] = useState('');
  const [createdId, setCreatedId] = useState(null);

  const handleFileChange = (side, e) => {
    const file = e.target.files[0];
    if (file) {
      const previewUrl = URL.createObjectURL(file);
      setSideUploads((prev) => ({
        ...prev,
        [side]: { file, preview: previewUrl },
      }));
    }
  };

  const removeSide = (side) => {
    setSideUploads((prev) => ({ ...prev, [side]: null }));
  };

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setGpsLat(pos.coords.latitude.toFixed(6));
          setGpsLon(pos.coords.longitude.toFixed(6));
        },
        (err) => {
          console.warn('Geolocation failed:', err.message);
        }
      );
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const uploadedEntries = Object.entries(sideUploads).filter(([_, val]) => val !== null);
    if (uploadedEntries.length === 0) {
      setError('Please attach at least one label image (e.g. Front Display Panel).');
      return;
    }

    setLoading(true);
    setShowPipeline(true);

    try {
      const formData = new FormData();
      formData.append('district', district);
      formData.append('state', state);
      if (storeName) formData.append('store_name', storeName);
      if (storeAddress) formData.append('store_address', storeAddress);
      if (gpsLat) formData.append('gps_latitude', parseFloat(gpsLat));
      if (gpsLon) formData.append('gps_longitude', parseFloat(gpsLon));
      if (inspectorNotes) formData.append('inspector_notes', inspectorNotes);

      uploadedEntries.forEach(([side, obj]) => {
        formData.append('images', obj.file);
        formData.append('sides', side);
      });

      const resp = await api.post('/inspections/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (resp.data && resp.data.id) {
        setCreatedId(resp.data.id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to initialize inspection docket. Please verify file formats.');
      setShowPipeline(false);
      setLoading(false);
    }
  };

  const onPipelineComplete = () => {
    if (createdId) {
      navigate(`/inspections/${createdId}`);
    }
  };

  const sides = [
    { key: 'front', title: 'Front Label (Principal Display)', required: true },
    { key: 'back', title: 'Back Panel (Statutory Declarations)', required: false },
    { key: 'left', title: 'Left Side Panel', required: false },
    { key: 'right', title: 'Right Side Panel', required: false },
    { key: 'top', title: 'Top / Seal Cap View', required: false },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Signature Multi-Stage Pipeline Modal Overlay */}
      {showPipeline && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-md p-4">
          <PipelineLoader
            intervalMs={650}
            onComplete={onPipelineComplete}
          />
        </div>
      )}

      {/* Header */}
      <GlassCard variant="default" className="p-6">
        <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-primary-600 mb-1">
          <Sparkles className="h-3.5 w-3.5" />
          <span>New Inspection Studio</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold font-display text-slate-900">
          Pre-Packaged Commodity Inspection
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Capture multi-side packaging images to initiate automated 12-step OpenCV preprocessing, dual-OCR spatial consensus, and Rule 6 compliance verification.
        </p>
      </GlassCard>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-rose-700 text-xs font-semibold flex items-center gap-2.5">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Establishment & Location Section */}
        <GlassCard variant="default" className="p-6 space-y-4">
          <h2 className="text-sm font-bold font-display text-slate-900 flex items-center gap-2">
            <Building2 className="w-4 h-4 text-primary-600" />
            <span>Establishment & Location Details</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">State / UT *</label>
              <input
                type="text"
                required
                value={state}
                onChange={(e) => setState(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-2xl px-3.5 py-2.5 text-slate-900 focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">District *</label>
              <input
                type="text"
                required
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-2xl px-3.5 py-2.5 text-slate-900 focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Store / Establishment Name</label>
              <input
                type="text"
                value={storeName}
                onChange={(e) => setStoreName(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-2xl px-3.5 py-2.5 text-slate-900 focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Store Address</label>
              <input
                type="text"
                value={storeAddress}
                onChange={(e) => setStoreAddress(e.target.value)}
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-2xl px-3.5 py-2.5 text-slate-900 focus:ring-2 focus:ring-primary-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="pt-2 flex items-center gap-3">
            <div className="flex-1 grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">GPS Latitude</label>
                <input
                  type="text"
                  value={gpsLat}
                  onChange={(e) => setGpsLat(e.target.value)}
                  className="w-full text-xs font-mono bg-slate-50 border border-slate-200 rounded-xl px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">GPS Longitude</label>
                <input
                  type="text"
                  value={gpsLon}
                  onChange={(e) => setGpsLon(e.target.value)}
                  className="w-full text-xs font-mono bg-slate-50 border border-slate-200 rounded-xl px-3 py-2"
                />
              </div>
            </div>
            <button
              type="button"
              onClick={handleGetLocation}
              className="mt-4 px-4 py-2.5 text-xs font-bold bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-2xl border border-blue-200 flex items-center gap-1.5 transition-colors"
            >
              <MapPin className="w-3.5 h-3.5 text-blue-600" />
              <span>Capture GPS</span>
            </button>
          </div>
        </GlassCard>

        {/* Multi-Side Image Capture Grid */}
        <GlassCard variant="default" className="p-6 space-y-4">
          <div>
            <h2 className="text-sm font-bold font-display text-slate-900 flex items-center gap-2">
              <Camera className="w-4 h-4 text-purple-600" />
              <span>Multi-Side Packaging Image Capture Studio</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Upload crisp label images. OpenCV engine deskews, eliminates glare, and enhances contrast automatically.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {sides.map((side) => {
              const current = sideUploads[side.key];
              return (
                <div
                  key={side.key}
                  className={`border-2 border-dashed rounded-3xl p-4 flex flex-col items-center justify-center text-center transition-all min-h-[200px] relative ${
                    current
                      ? 'border-emerald-500 bg-emerald-50/30'
                      : 'border-slate-200 hover:border-primary-400 bg-slate-50/50'
                  }`}
                >
                  {current ? (
                    <div className="w-full h-full flex flex-col items-center">
                      <img
                        src={current.preview}
                        alt={side.title}
                        className="w-full h-32 object-cover rounded-2xl shadow-sm border border-slate-200"
                      />
                      <span className="text-xs font-bold text-emerald-800 mt-2 flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                        <span>{side.title}</span>
                      </span>
                      <button
                        type="button"
                        onClick={() => removeSide(side.key)}
                        className="absolute top-2 right-2 p-1.5 rounded-full bg-rose-500 text-white hover:bg-rose-600 shadow-sm"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ) : (
                    <label className="cursor-pointer w-full h-full flex flex-col items-center justify-center py-4">
                      <div className="p-3.5 bg-white rounded-2xl shadow-soft border border-slate-100 mb-2">
                        <Upload className="w-5 h-5 text-primary-600" />
                      </div>
                      <span className="text-xs font-bold text-slate-800">{side.title}</span>
                      <span className="text-[10px] text-slate-400 mt-0.5 font-medium">
                        {side.required ? 'Mandatory Display Panel' : 'Optional Additional Panel'}
                      </span>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleFileChange(side.key, e)}
                        className="hidden"
                      />
                    </label>
                  )}
                </div>
              );
            })}
          </div>
        </GlassCard>

        {/* Inspector Observations */}
        <GlassCard variant="default" className="p-6">
          <label className="block text-xs font-semibold text-slate-700 mb-1.5">
            Inspector Field Observations / Enforcement Notes
          </label>
          <textarea
            rows={2}
            value={inspectorNotes}
            onChange={(e) => setInspectorNotes(e.target.value)}
            className="w-full text-xs bg-slate-50 border border-slate-200 rounded-2xl p-3 text-slate-900 focus:ring-2 focus:ring-primary-500 focus:outline-none"
          />
        </GlassCard>

        {/* Action Buttons */}
        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={() => navigate('/inspections')}
            className="px-5 py-2.5 text-xs font-bold bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-2xl transition-colors shadow-soft"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={loading}
            className="px-7 py-3 text-xs font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:opacity-95 text-white rounded-2xl shadow-tinted-blue flex items-center space-x-2 transition-transform hover:scale-105 active:scale-95 disabled:opacity-50"
          >
            <span>Upload & Run AI Enforcement Pipeline</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
export default NewInspectionPage;
