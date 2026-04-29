import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import axios from 'axios';
import { useToast } from './ToastContext';

// ─── Types ────────────────────────────────────────────────────────────────────
interface AuthUser {
  id: number;
  email: string;
  created_at: string;
}

interface AuthContextType {
  user: AuthUser | null;
  accessToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

// ─── Context ──────────────────────────────────────────────────────────────────
const AuthContext = createContext<AuthContextType | null>(null);

const API_BASE = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api').replace(/\/api\/?$/, '');

// ─── Axios Interceptor: auto-attach Bearer token to every request ─────────────
let _accessToken: string | null = null;

axios.interceptors.request.use((config) => {
  if (_accessToken) {
    config.headers.Authorization = `Bearer ${_accessToken}`;
  }
  return config;
});

// ─── Provider ─────────────────────────────────────────────────────────────────
export function AuthProvider({ children }: { children: ReactNode }) {
  const toast = useToast();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // ─── Global API Error Interceptor ───────────────────────────────────────────
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        // Network errors or CORS
        if (!error.response) {
          toast.error('NETWORK_ERROR', 'Cannot connect to server. Check your connection.');
          return Promise.reject(error);
        }
        
        const status = error.response.status;
        const data = error.response.data;
        const isAuthRoute = error.config?.url?.includes('/api/auth/');
        
        if (status === 401 && !isAuthRoute) {
          toast.error('SESSION_EXPIRED', 'Your access token has expired. Please log in again.');
          clearAuth();
        } else if (status === 429) {
          toast.warning('RATE_LIMIT_EXCEEDED', data?.message || 'Too many requests. Please slow down.');
        } else if (status >= 500) {
          toast.error('SYSTEM_ERROR', data?.message || 'An internal server error occurred.');
        }
        
        return Promise.reject(error);
      }
    );
    
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, [toast]);

  // Persist token in sessionStorage (cleared when tab closes — safer than localStorage)
  const persistToken = (token: string) => {
    _accessToken = token;
    setAccessToken(token);
    sessionStorage.setItem('access_token', token);
  };

  const clearAuth = () => {
    _accessToken = null;
    setAccessToken(null);
    setUser(null);
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
  };

  // On app load: rehydrate session from sessionStorage
  useEffect(() => {
    const savedToken = sessionStorage.getItem('access_token');
    if (savedToken) {
      _accessToken = savedToken;
      setAccessToken(savedToken);
      // Verify the token is still valid by hitting /me
      axios.get(`${API_BASE}/api/auth/me`)
        .then(res => {
          if (res.data.status === 'success') setUser(res.data.user);
          else clearAuth();
        })
        .catch(() => clearAuth())
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await axios.post(`${API_BASE}/api/auth/login`, { email, password });
    if (res.data.status !== 'success') throw new Error(res.data.message);
    persistToken(res.data.access_token);
    sessionStorage.setItem('refresh_token', res.data.refresh_token);
    setUser(res.data.user);
  }, []);

  const register = useCallback(async (email: string, password: string) => {
    const res = await axios.post(`${API_BASE}/api/auth/register`, { email, password });
    if (res.data.status !== 'success') throw new Error(res.data.message);
    persistToken(res.data.access_token);
    sessionStorage.setItem('refresh_token', res.data.refresh_token);
    setUser(res.data.user);
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    // Also clear the placement profile from local storage
    localStorage.removeItem('user_id');
  }, []);

  return (
    <AuthContext.Provider value={{
      user,
      accessToken,
      isLoading,
      isAuthenticated: !!user,
      login,
      register,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────────────────────
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
