import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Badge } from '../components/Badge';
import { BookOpen, Scale, AlertCircle, FileText, CheckCircle2, Shield } from 'lucide-react';

export const RulesPage = () => {
  const [activeVersion, setActiveVersion] = useState(null);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRules = async () => {
      setLoading(true);
      try {
        const [vRes, rRes] = await Promise.all([
          api.get('/rules/version/active'),
          api.get('/rules/'),
        ]);
        setActiveVersion(vRes.data);
        setRules(rRes.data || []);
      } catch (err) {
        console.error('Error fetching rules:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRules();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-amber-600">
            <Scale className="w-4 h-4 text-amber-500" />
            Statutory Legal Framework
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">
            Legal Metrology Rules & Gazette Repository
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Active statutory rules, mandatory packaging declarations, and statutory penalty schedules.
          </p>
        </div>

        {activeVersion && (
          <div className="bg-slate-900 text-white p-3 rounded-xl flex items-center gap-3">
            <Shield className="w-6 h-6 text-amber-400 shrink-0" />
            <div>
              <div className="text-[10px] uppercase font-mono text-slate-400">ACTIVE RULESET</div>
              <div className="text-xs font-bold font-mono text-amber-400">{activeVersion.version_tag}</div>
            </div>
          </div>
        )}
      </div>

      {/* Rules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {loading ? (
          <div className="col-span-2 py-16 text-center text-slate-400">
            <div className="inline-block w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="block mt-2 text-xs">Loading statutory provisions...</span>
          </div>
        ) : (
          rules.map((rule) => (
            <div key={rule.id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <div className="flex justify-between items-start">
                <div>
                  <span className="font-mono text-xs font-bold text-amber-600 block">{rule.rule_code}</span>
                  <h3 className="text-base font-bold text-slate-900 mt-0.5">{rule.title}</h3>
                </div>
                <Badge variant={rule.severity === 'critical' ? 'danger' : 'warning'} size="xs">
                  {rule.severity.toUpperCase()}
                </Badge>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl text-xs space-y-1.5 border border-slate-100">
                <div>
                  <span className="text-slate-500 font-semibold">Statutory Source: </span>
                  <span className="font-medium text-slate-900">{rule.statutory_source}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-semibold">Penal Provision: </span>
                  <span className="font-medium text-slate-900">{rule.statutory_penalty_source}</span>
                </div>
                <div>
                  <span className="text-slate-500 font-semibold">Field Targeted: </span>
                  <span className="font-mono bg-slate-200 px-1.5 py-0.5 rounded text-[10px] text-slate-800">
                    {rule.field_to_validate}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-600 leading-relaxed">{rule.description}</p>

              <div className="pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">1st Offence Fine</span>
                  <span className="font-bold text-slate-800">{rule.penalty_first_offence || 'Up to ₹25,000'}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold block">Repeat Offence Penalty</span>
                  <span className="font-bold text-rose-700">{rule.penalty_repeat_offence || 'Up to ₹50,000 / Jail'}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
