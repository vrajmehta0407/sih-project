import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Badge } from '../components/Badge';
import {
  Scale,
  ShieldCheck,
  ShieldAlert,
  CheckCircle2,
  Calendar,
  MapPin,
  Building2,
  AlertTriangle,
  QrCode,
  FileText,
  Lock,
} from 'lucide-react';

export const VerifyQRPage = () => {
  const { qrToken } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const verifyToken = async () => {
      setLoading(true);
      setError('');
      try {
        const resp = await axios.get(`/api/v1/inspections/verify/${qrToken}`);
        setData(resp.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Invalid or unrecognized QR verification token.');
      } finally {
        setLoading(false);
      }
    };

    if (qrToken) {
      verifyToken();
    }
  }, [qrToken]);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 py-12 px-4 sm:px-6 lg:px-8 flex flex-col justify-center items-center">
      <div className="max-w-2xl w-full space-y-6">
        {/* Government Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-2xl bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20">
            <Scale className="w-8 h-8" />
          </div>
          <h1 className="text-xl font-extrabold text-white tracking-wide">
            GOVERNMENT OF INDIA • LEGAL METROLOGY DIVISION
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            National Public Verification Gateway • Indian Evidence Act / BSA 2023 Compliant
          </p>
        </div>

        {loading ? (
          <div className="bg-slate-950 p-8 rounded-2xl border border-slate-800 text-center">
            <div className="inline-block w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-sm text-slate-400 mt-3">Verifying cryptographic chain-of-custody seal...</p>
          </div>
        ) : error ? (
          <div className="bg-rose-950/40 p-8 rounded-2xl border border-rose-800 text-center space-y-4">
            <ShieldAlert className="w-12 h-12 text-rose-500 mx-auto" />
            <h2 className="text-lg font-bold text-rose-300">Verification Failed</h2>
            <p className="text-xs text-rose-400 max-w-md mx-auto">{error}</p>
            <Link
              to="/login"
              className="inline-block px-4 py-2 text-xs font-semibold bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700"
            >
              Go to Officer Portal
            </Link>
          </div>
        ) : data ? (
          <div className="bg-slate-950 rounded-2xl border border-slate-800 p-6 sm:p-8 space-y-6 shadow-2xl">
            {/* Authenticity Certificate Banner */}
            <div className="p-4 bg-emerald-950/50 border border-emerald-500/40 rounded-xl flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-500/20 rounded-lg text-emerald-400">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-emerald-300">AUTHENTIC STATUTORY RECORD CERTIFIED</h3>
                  <p className="text-xs text-emerald-400/80">Tamper-Proof SHA-256 Digest Confirmed</p>
                </div>
              </div>
              <Badge variant={data.compliance_status === 'compliant' ? 'success' : 'danger'}>
                {data.compliance_status.toUpperCase()}
              </Badge>
            </div>

            {/* SHA-256 Digest */}
            <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-1">
              <div className="flex justify-between text-[11px] font-mono text-slate-400">
                <span>CHAIN OF CUSTODY SHA-256 HASH</span>
                <Lock className="w-3.5 h-3.5 text-amber-500" />
              </div>
              <p className="font-mono text-xs text-amber-400 break-all">{data.chain_of_custody_hash}</p>
            </div>

            {/* Inspection Details Matrix */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
              <div className="p-3.5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-500 block font-medium">Statutory Docket Number</span>
                <span className="text-sm font-bold text-white font-mono">{data.docket_number}</span>
              </div>
              <div className="p-3.5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-500 block font-medium">Inspection Docket #</span>
                <span className="text-sm font-bold text-white font-mono">{data.inspection_number}</span>
              </div>
              <div className="p-3.5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-500 block font-medium">Inspected Commodity</span>
                <span className="text-sm font-bold text-white">{data.product_name || 'Pre-packaged Commodity'}</span>
              </div>
              <div className="p-3.5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-500 block font-medium">Declared Manufacturer / Brand</span>
                <span className="text-sm font-bold text-white">{data.manufacturer_name || 'N/A'}</span>
              </div>
              <div className="p-3.5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-500 block font-medium">Establishment / Shop</span>
                <span className="text-sm font-bold text-white">{data.store_name || 'Retail Market Outlet'}</span>
              </div>
              <div className="p-3.5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-1">
                <span className="text-slate-500 block font-medium">Jurisdiction & Date</span>
                <span className="text-sm font-bold text-white">{data.jurisdiction} • {data.inspection_date}</span>
              </div>
            </div>

            {/* Violations Summary (if any) */}
            {data.violations?.length > 0 && (
              <div className="p-4 bg-rose-950/30 border border-rose-800/40 rounded-xl space-y-3">
                <div className="flex items-center gap-2 text-rose-400 font-bold text-xs">
                  <AlertTriangle className="w-4 h-4" />
                  Recorded Statutory Violations ({data.total_violations}):
                </div>
                <div className="space-y-2">
                  {data.violations.map((v, i) => (
                    <div key={i} className="p-2.5 bg-slate-900 rounded-lg text-xs flex justify-between items-center">
                      <div>
                        <span className="font-bold text-white block">{v.title}</span>
                        <span className="text-[11px] font-mono text-slate-400">{v.section}</span>
                      </div>
                      <Badge variant={v.severity === 'critical' ? 'danger' : 'warning'} size="xs">
                        {v.severity.toUpperCase()}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-4 border-t border-slate-800 text-center">
              <Link
                to="/login"
                className="text-xs font-semibold text-amber-500 hover:text-amber-400"
              >
                Access Official Enforcement Officer Portal →
              </Link>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};
