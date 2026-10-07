"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";
import { api, ApiError, clearTokens, getAccessToken, SESSION_EXPIRED_EVENT, setTokens } from "@/lib/api";
import type { LoginRequest, RegisterRequest, UserOut } from "@/types";

interface AuthContextValue {
  user: UserOut | null;
  isLoading: boolean;
  /** True when a stored session exists but the API could not be reached (or errored), so we could not verify it. */
  unreachable: boolean;
  /** True after a session ended because its tokens expired or were rejected. */
  sessionExpired: boolean;
  error: string | null;
  login: (body: LoginRequest) => Promise<UserOut>;
  register: (body: RegisterRequest) => Promise<UserOut>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [unreachable, setUnreachable] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);

  const loadUser = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const me = await api.auth.me();
      setUser(me);
      setUnreachable(false);
    } catch (err) {
      if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
        clearTokens();
        setUser(null);
        setUnreachable(false);
      } else {
        // Network failure or server error: keep the session so a retry can restore it.
        setUnreachable(true);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  // Fired by lib/api when a request got a 401 that a token refresh could not fix.
  useEffect(() => {
    const onExpired = () => {
      setUser(null);
      setUnreachable(false);
      setSessionExpired(true);
    };
    window.addEventListener(SESSION_EXPIRED_EVENT, onExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, onExpired);
  }, []);

  const login = useCallback(async (body: LoginRequest) => {
    setError(null);
    try {
      const tokens = await api.auth.login(body);
      setTokens(tokens.access_token, tokens.refresh_token);
      const me = await api.auth.me();
      setUser(me);
      setSessionExpired(false);
      return me;
    } catch (err) {
      const message = err instanceof ApiError ? err.detail : "Unable to log in.";
      setError(message);
      throw err;
    }
  }, []);

  const register = useCallback(async (body: RegisterRequest) => {
    setError(null);
    try {
      const tokens = await api.auth.register(body);
      setTokens(tokens.access_token, tokens.refresh_token);
      const me = await api.auth.me();
      setUser(me);
      return me;
    } catch (err) {
      const message = err instanceof ApiError ? err.detail : "Unable to sign up.";
      setError(message);
      throw err;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.auth.logout();
    } catch {
      // ignore network errors on logout
    } finally {
      clearTokens();
      setUser(null);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, isLoading, unreachable, sessionExpired, error, login, register, logout, refreshUser: loadUser }),
    [user, isLoading, unreachable, sessionExpired, error, login, register, logout, loadUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
