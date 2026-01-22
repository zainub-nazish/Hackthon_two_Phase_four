"use client";

import { useEffect, useState, useCallback } from "react";
import { getSession, signOut as betterAuthSignOut } from "@/lib/auth-client";
import type { AuthState, User } from "@/types";

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function checkSession() {
      try {
        const session = await getSession();

        if (!mounted) return;

        if (session?.data?.user) {
          const user: User = {
            id: session.data.user.id,
            email: session.data.user.email,
            name: session.data.user.name,
          };
          setAuthState({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } else {
          setAuthState({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
        }
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : "Failed to check session");
        setAuthState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    }

    checkSession();

    return () => {
      mounted = false;
    };
  }, []);

  const signOut = useCallback(async () => {
    try {
      await betterAuthSignOut();
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
      // Redirect to login after sign out
      window.location.href = "/login";
    } catch (err) {
      console.error("Sign out error:", err);
    }
  }, []);

  return {
    ...authState,
    signOut,
    error,
  };
}
