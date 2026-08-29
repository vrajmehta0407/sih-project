import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    // Restore from localStorage on initial load
    const stored = localStorage.getItem('lm_user_profile');
    try { return stored ? JSON.parse(stored) : null; } catch { return null; }
  });
  const [token, setToken] = useState(() => localStorage.getItem('lm_auth_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verifySession = async () => {
      const storedToken = localStorage.getItem('lm_auth_token');
      if (!storedToken) {
        setLoading(false);
        return;
      }
      try {
        // GET /auth/me returns ResponseEnvelope → { success, data: UserResponse }
        const resp = await api.get('/auth/me');
        const profile = resp.data?.data || resp.data;
        setUser(profile);
        localStorage.setItem('lm_user_profile', JSON.stringify(profile));
      } catch (err) {
        console.warn('Session invalid, clearing auth:', err.message);
        localStorage.removeItem('lm_auth_token');
        localStorage.removeItem('lm_user_profile');
        setUser(null);
        setToken(null);
      } finally {
        setLoading(false);
      }
    };

    verifySession();
  }, []);

  const login = async (email, password) => {
    // Use /auth/login/json — accepts JSON body, returns token directly (no envelope)
    const resp = await api.post('/auth/login/json', { email, password });
    const tokenData = resp.data;

    if (!tokenData?.access_token) {
      throw new Error('No access token received from server.');
    }

    const jwtToken = tokenData.access_token;
    localStorage.setItem('lm_auth_token', jwtToken);
    setToken(jwtToken);

    // Build user profile from the token response payload
    const profile = {
      id: tokenData.user_id,
      email: tokenData.email,
      full_name: tokenData.full_name,
      role: tokenData.role,
    };

    setUser(profile);
    localStorage.setItem('lm_user_profile', JSON.stringify(profile));

    // Optionally fetch full profile (badge number, jurisdiction etc.)
    try {
      const meResp = await api.get('/auth/me');
      const fullProfile = meResp.data?.data || meResp.data;
      setUser(fullProfile);
      localStorage.setItem('lm_user_profile', JSON.stringify(fullProfile));
      return fullProfile;
    } catch {
      return profile;
    }
  };

  const logout = () => {
    localStorage.removeItem('lm_auth_token');
    localStorage.removeItem('lm_user_profile');
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
