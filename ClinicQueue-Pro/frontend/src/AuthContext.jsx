import { createContext, useCallback, useEffect, useMemo, useState } from "react";

export const AuthContext = createContext();
const API_URL = import.meta.env.VITE_API_URL || "";

async function readError(response) {
  try { const body = await response.json(); return body.detail || "Request failed"; }
  catch { return `Request failed (${response.status})`; }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("user") || "null"));
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function validateSession() {
      if (!token) { setLoading(false); return; }
      try {
        const response = await fetch(`${API_URL}/api/auth/me`, { headers: { Authorization: `Bearer ${token}` } });
        if (!response.ok) throw new Error("Session expired");
        const freshUser = await response.json(); setUser(freshUser); localStorage.setItem("user", JSON.stringify(freshUser));
      } catch { setToken(null); setUser(null); localStorage.removeItem("token"); localStorage.removeItem("user"); }
      finally { setLoading(false); }
    }
    validateSession();
  }, [token]);

  const saveSession = useCallback((data) => { setToken(data.access_token); setUser(data.user); localStorage.setItem("token", data.access_token); localStorage.setItem("user", JSON.stringify(data.user)); }, []);
  const login = useCallback(async (email, password) => { try { setError(null); const res = await fetch(`${API_URL}/api/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) }); if (!res.ok) throw new Error(await readError(res)); saveSession(await res.json()); return { success: true }; } catch (err) { setError(err.message); return { success: false, error: err.message }; } }, [saveSession]);
  const register = useCallback(async (formData) => { try { setError(null); const res = await fetch(`${API_URL}/api/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(formData) }); if (!res.ok) throw new Error(await readError(res)); saveSession(await res.json()); return { success: true }; } catch (err) { setError(err.message); return { success: false, error: err.message }; } }, [saveSession]);
  const logout = useCallback(() => { setUser(null); setToken(null); localStorage.removeItem("token"); localStorage.removeItem("user"); setError(null); }, []);
  const apiCall = useCallback(async (endpoint, options = {}) => { const headers = { "Content-Type": "application/json", ...(options.headers || {}) }; if (token) headers.Authorization = `Bearer ${token}`; const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers }); if (!res.ok) throw new Error(await readError(res)); return res.status === 204 ? null : res.json(); }, [token]);
  const value = useMemo(() => ({ user, token, loading, error, login, register, logout, apiCall }), [user, token, loading, error, login, register, logout, apiCall]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
