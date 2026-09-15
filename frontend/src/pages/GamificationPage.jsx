import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import {
  Trophy,
  Award,
  Medal,
  Crown,
  Star,
  Flame,
  TrendingUp,
  Gift,
  RefreshCw,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';

const LEVEL_THRESHOLDS = [0, 100, 250, 500, 900, 1500];

const levelInfo = (points) => {
  let level = 1;
  for (let i = 0; i < LEVEL_THRESHOLDS.length; i++) {
    if (points >= LEVEL_THRESHOLDS[i]) level = i + 1;
  }
  const cap = LEVEL_THRESHOLDS[level] ?? LEVEL_THRESHOLDS[LEVEL_THRESHOLDS.length - 1];
  const floor = LEVEL_THRESHOLDS[level - 1] ?? 0;
  const progress = Math.min(100, Math.round(((points - floor) / (cap - floor)) * 100));
  return { level, progress };
};

const BADGES = [
  { icon: Star, label: 'First Inspection', color: 'bg-blue-50 text-blue-600' },
  { icon: Award, label: 'Compliance Star', color: 'bg-violet-50 text-violet-600' },
  { icon: Medal, label: '10× Inspector', color: 'bg-emerald-50 text-emerald-600' },
  { icon: Crown, label: 'District Leader', color: 'bg-amber-50 text-amber-600' },
  { icon: Flame, label: 'On Fire Streak', color: 'bg-rose-50 text-rose-600' },
  { icon: Gift, label: 'Problem Solver', color: 'bg-pink-50 text-pink-600' },
];

export const GamificationPage = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [awardPoints, setAwardPoints] = useState(10);
  const [awardReason, setAwardReason] = useState('Exceptional inspection');
  const [awarding, setAwarding] = useState(false);
  const [toast, setToast] = useState('');

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/gamification/profile/${userId()}`);
      const data = res.data?.data ?? res.data;
      setProfile(data);
    } catch (err) {
      setProfile(null);
      setError(err.response?.data?.detail || 'Could not load gamification profile.');
    } finally {
      setLoading(false);
    }
  };

  const userId = () => {
    try {
      const raw = localStorage.getItem('lm_user_profile');
      if (!raw) return user?.id || '';
      const parsed = JSON.parse(raw);
      return parsed?.id || user?.id || '';
    } catch {
      return user?.id || '';
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const award = async () => {
    setAwarding(true);
    try {
      await api.post('/gamification/points/award', {
        points: awardPoints,
        reason: awardReason,
      });
      setToast(`Awarded ${awardPoints} points: ${awardReason}`);
      setTimeout(() => setToast(''), 3000);
      fetchProfile();
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not award points.');
    } finally {
      setAwarding(false);
    }
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <RefreshCw className="h-8 w-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  const points = profile?.total_points ?? 0;
  const { level, progress } = levelInfo(points);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-mesh-vibrant rounded-3xl p-6 sm:p-8 border border-white/60 shadow-soft">
        <div className="flex items-center space-x-3 mb-3">
          <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-blue-600 via-violet-600 to-pink-600 flex items-center justify-center text-white shadow-tinted-blue">
            <Trophy className="h-5 w-5" />
          </div>
          <div>
            <h1 className="font-display text-2xl font-extrabold text-slate-900">
              Gamification & Rewards
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              Officer achievement, streak and leaderboard progression
            </p>
          </div>
        </div>
        {toast && (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span>{toast}</span>
          </span>
        )}
      </div>

      {error && (
        <div className="px-4 py-3 rounded-2xl text-sm font-semibold bg-rose-50 text-rose-700 border border-rose-200">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Sparkles, label: 'Total Points', value: points, color: 'from-blue-500 to-violet-500' },
          { icon: Trophy, label: 'Current Level', value: `Lv ${level}`, color: 'from-violet-500 to-pink-500' },
          { icon: Flame, label: 'Day Streak', value: profile?.current_streak ?? 0, color: 'from-orange-500 to-rose-500' },
          { icon: TrendingUp, label: 'Inspections', value: profile?.inspections_count ?? 0, color: 'from-emerald-500 to-teal-500' },
        ].map((s, i) => {
          const Icon = s.icon;
          return (
            <div
              key={i}
              className="rounded-3xl bg-white border border-slate-200 shadow-sm p-4"
            >
              <div
                className={`h-10 w-10 rounded-2xl bg-gradient-to-br ${s.color} flex items-center justify-center text-white shadow-sm mb-3`}
              >
                <Icon className="h-5 w-5" />
              </div>
              <p className="text-2xl font-extrabold text-slate-900">{s.value}</p>
              <p className="text-xs font-semibold text-slate-500">{s.label}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Level Progress */}
        <div className="lg:col-span-2 rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
          <h2 className="font-display text-lg font-bold text-slate-900 mb-4">
            Level Progress
          </h2>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-bold text-slate-700">Level {level}</span>
            <span className="text-xs font-bold text-violet-600">{progress}%</span>
          </div>
          <div className="h-4 w-full rounded-full bg-slate-100 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-blue-600 via-violet-600 to-pink-600 transition-all duration-700"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-slate-400 mt-2">
            {points} points earned · {profile?.longest_streak ?? 0} longest streak
          </p>

          <h3 className="font-display text-base font-bold text-slate-900 mt-6 mb-3">
            Earned Badges
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {(profile?.earned_badges?.length
              ? profile.earned_badges
              : BADGES.map((b, i) => ({ name: b.label, earned: i < Math.min(3, level) }))
            ).map((badge, i) => {
              const def = BADGES[i % BADGES.length];
              const Icon = def.icon;
              const earned = badge.earned !== false;
              return (
                <div
                  key={i}
                  className={`flex items-center space-x-2.5 p-3 rounded-2xl border ${
                    earned
                      ? 'bg-gradient-to-br from-violet-50 to-pink-50 border-violet-200'
                      : 'bg-slate-50 border-slate-100 opacity-50'
                  }`}
                >
                  <span
                    className={`h-9 w-9 rounded-xl flex items-center justify-center ${
                      def.color
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                  </span>
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-slate-800 truncate">
                      {badge.name}
                    </p>
                    <p className="text-[10px] text-slate-400">
                      {earned ? 'Earned' : 'Locked'}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Award */}
        <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-5 sm:p-6">
          <h2 className="font-display text-lg font-bold text-slate-900 mb-1">
            Award Points
          </h2>
          <p className="text-xs text-slate-500 mb-5">
            Recognize an officer with bonus achievement points.
          </p>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                Points
              </label>
              <input
                type="number"
                min="1"
                value={awardPoints}
                onChange={(e) => setAwardPoints(Number(e.target.value))}
                className="w-full px-3 py-2.5 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1 uppercase tracking-wide">
                Reason
              </label>
              <input
                value={awardReason}
                onChange={(e) => setAwardReason(e.target.value)}
                className="w-full px-3 py-2.5 rounded-2xl bg-white border border-slate-200 shadow-sm text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              />
            </div>
            <button
              onClick={award}
              disabled={awarding || awardPoints < 1}
              className="w-full inline-flex items-center justify-center space-x-2 px-4 py-3 rounded-2xl bg-gradient-to-r from-violet-600 to-pink-600 text-white font-bold text-sm shadow-tinted-violet hover:opacity-95 transition-opacity disabled:opacity-60"
            >
              {awarding ? (
                <RefreshCw className="h-4 w-4 animate-spin" />
              ) : (
                <Gift className="h-4 w-4" />
              )}
              <span>{awarding ? 'Awarding...' : 'Award Points'}</span>
            </button>
          </div>
        </div>
      </div>

      <div className="text-right text-[11px] text-slate-400 font-medium">
        Profile & badges sync via /gamification/profile/:id
      </div>
    </div>
  );
};

export default GamificationPage;
