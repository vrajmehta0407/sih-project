import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  Mic,
  Volume2,
  Send,
  RefreshCw,
  AudioLines,
  User,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Activity,
} from 'lucide-react';

export const VoiceReportPage = () => {
  const { user } = useAuth();
  const [transcript, setTranscript] = useState('');
  const [voiceInput, setVoiceInput] = useState('');
  const [listening, setListening] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [supported, setSupported] = useState(
    typeof window !== 'undefined' && !!(window.SpeechRecognition || window.webkitSpeechRecognition)
  );

  const startListening = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      setSupported(false);
      setError('Speech recognition is not supported in this browser.');
      return;
    }
    const rec = new SR();
    rec.lang = 'en-IN';
    rec.interimResults = true;
    rec.continuous = true;
    setListening(true);
    setError('');
    let finalText = '';
    rec.onresult = (e) => {
      let interim = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const res = e.results[i];
        if (res.isFinal) finalText += res[0].transcript + ' ';
        else interim += res[0].transcript;
      }
      setVoiceInput((finalText + interim).trim());
    };
    rec.onerror = () => {
      setListening(false);
      setError('Microphone unavailable or permission denied.');
    };
    rec.onend = () => setListening(false);
    rec.start();
    window.__lmRec = rec;
  };

  const stopListening = () => {
    if (window.__lmRec) window.__lmRec.stop();
    setListening(false);
  };

  const submit = async () => {
    const text = voiceInput || transcript;
    if (!text.trim()) {
      setError('Please speak into the microphone or type a transcript.');
      return;
    }
    setSubmitting(true);
    setError('');
    setResult(null);
    try {
      const res = await api.post('/citizen/voice/transcript', {
        transcript: text.trim(),
      });
      const data = res.data?.data ?? res.data ?? res;
      setResult(data);
      setTranscript(text.trim());
      setVoiceInput('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not submit the voice report.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-mesh-vibrant rounded-3xl p-6 sm:p-8 border border-white/60 shadow-soft">
        <div className="flex items-center space-x-3 mb-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-violet-600 to-pink-600 flex items-center justify-center text-white shadow-tinted-blue">
            <Mic className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-extrabold text-slate-900">
              Voice Report
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              Dictate a citizen complaint, it becomes a structured record
            </p>
          </div>
        </div>
        <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-white/70 text-emerald-700 border border-emerald-200">
          <Activity className="h-3 w-3" />
          <span>Citizen voice → structured report</span>
        </span>
      </div>

      {error && (
        <div className="px-4 py-3 rounded-2xl text-sm font-semibold bg-rose-50 text-rose-700 border border-rose-200 flex items-center space-x-2">
          <AlertTriangle className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input */}
        <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
          <h2 className="font-display text-lg font-bold text-slate-900 mb-1">
            Live Dictation
          </h2>
          <p className="text-xs text-slate-500 mb-5">
            Speak naturally — the assistant transcribes and normalizes the report.
          </p>

          <div className="flex items-center justify-center py-8">
            <button
              onClick={listening ? stopListening : startListening}
              className={`relative h-24 w-24 rounded-full flex items-center justify-center transition-all ${
                listening
                  ? 'bg-gradient-to-tr from-rose-500 to-pink-600 text-white shadow-tinted-rose animate-pulse'
                  : 'bg-gradient-to-tr from-blue-600 to-violet-600 text-white shadow-tinted-blue hover:scale-105'
              }`}
            >
              {listening ? (
                <AudioLines className="h-9 w-9" />
              ) : (
                <Mic className="h-9 w-9" />
              )}
            </button>
          </div>
          <p className="text-center text-xs font-medium text-slate-400 mb-4">
            {listening
              ? 'Listening... speak your report'
              : supported
                ? 'Tap to start dictation'
                : 'Dictation unsupported — type below'}
          </p>

          {voiceInput && (
            <div className="p-3 rounded-2xl bg-blue-50 border border-blue-100 text-sm text-slate-700 mb-4 whitespace-pre-wrap">
              {voiceInput}
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
              Or type the report
            </label>
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              rows={4}
              placeholder="Shop on MG Road is selling packaged goods without mandatory net quantity and manufacturing date..."
              className="w-full px-3 py-2.5 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40 resize-none"
            />
          </div>

          <button
            onClick={submit}
            disabled={submitting}
            className="mt-4 w-full inline-flex items-center justify-center space-x-2 px-4 py-3 rounded-2xl bg-gradient-to-r from-blue-600 via-violet-600 to-pink-600 text-white font-bold text-sm shadow-tinted-blue hover:opacity-95 transition-opacity disabled:opacity-60"
          >
            {submitting ? (
              <RefreshCw className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
            <span>{submitting ? 'Processing...' : 'Submit Report'}</span>
          </button>
        </div>

        {/* Result */}
        <div className="rounded-3xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100 shadow-sm p-5 sm:p-6">
          <h2 className="font-display text-lg font-bold text-slate-900 mb-1">
            Structured Result
          </h2>
          <p className="text-xs text-slate-500 mb-5">
            How the voice transcript was normalized.
          </p>

          {result ? (
            <div className="space-y-3">
              {[
                { icon: User, label: 'Citizen', value: result.citizen_name || result.reporter_name || '—' },
                { icon: FileText, label: 'Category', value: result.category || result.issue_type || 'General' },
                { icon: Volume2, label: 'Transcript', value: result.transcript || result.summary || '—' },
                { icon: CheckCircle2, label: 'Status', value: result.status || 'Received' },
              ].map((r, i) => {
                const Icon = r.icon;
                return (
                  <div key={i} className="p-3 rounded-2xl bg-white border border-slate-200 shadow-sm">
                    <p className="flex items-center space-x-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-1">
                      <Icon className="h-3 w-3" />
                      <span>{r.label}</span>
                    </p>
                    <p className="text-sm text-slate-700">{r.value}</p>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-14">
              <div className="h-14 w-14 rounded-2xl bg-white flex items-center justify-center text-emerald-400 shadow-sm mx-auto mb-3">
                <Volume2 className="h-7 w-7" />
              </div>
              <p className="text-sm font-semibold text-slate-500">
                Submitted reports appear here
              </p>
            </div>
          )}
        </div>
      </div>

      <div className="text-right text-[11px] text-slate-400 font-medium">
        Reports sync via /citizen/voice/transcript ({user?.full_name || 'officer'})
      </div>
    </div>
  );
};

export default VoiceReportPage;
