import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

const TOKEN_KEY = 'robotics_auth_token';
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const { siteConfig } = useDocusaurusContext();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const getApiUrl = useCallback(
    () => siteConfig?.customFields?.chatApiUrl || 'http://localhost:8000',
    [siteConfig]
  );

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setLoading(false);
      return;
    }
    fetch(`${getApiUrl()}/api/v1/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data) setUser(data);
        else localStorage.removeItem(TOKEN_KEY);
      })
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false));
  }, [getApiUrl]);

  const signup = useCallback(
    async (email, name, codeId, password, softwareBg = '', hardwareBg = '') => {
      const r = await fetch(`${getApiUrl()}/api/v1/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          name,
          code_id: codeId,
          password,
          software_background: softwareBg,
          hardware_background: hardwareBg,
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || 'Signup failed');
      localStorage.setItem(TOKEN_KEY, data.token);
      setUser(data.user);
      return data.user;
    },
    [getApiUrl]
  );

  const signin = useCallback(
    async (email, password) => {
      const r = await fetch(`${getApiUrl()}/api/v1/auth/signin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || 'Sign in failed');
      localStorage.setItem(TOKEN_KEY, data.token);
      setUser(data.user);
      return data.user;
    },
    [getApiUrl]
  );

  const signout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }, []);

  const getToken = useCallback(() => localStorage.getItem(TOKEN_KEY), []);

  return (
    <AuthContext.Provider value={{ user, loading, signup, signin, signout, getToken, getApiUrl }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
