/**
 * Better Auth client-side helper.
 *
 * Provides client-side authentication utilities for React components.
 * Build: 2026-01-29-v5 - Hardcoded production URL
 */

import { createAuthClient } from "better-auth/react";

// HARDCODED: Production URL for Vercel deployment
// This MUST match your Vercel deployment URL
const PRODUCTION_URL = "https://frontend-delta-two-31.vercel.app";

// Create auth client with hardcoded production URL
// For local dev, this will cause CORS errors but that's expected
export const authClient = createAuthClient({
  baseURL: PRODUCTION_URL,
});

// Re-export commonly used methods
export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;

/**
 * Get the current session token for API requests.
 *
 * The backend will verify this token by calling Better Auth's session endpoint.
 *
 * @returns Session token string or null if not authenticated
 */
export async function getAuthToken(): Promise<string | null> {
  try {
    const session = await getSession();
    if (session?.data?.session?.token) {
      return session.data.session.token;
    }
    return null;
  } catch {
    return null;
  }
}

/**
 * Check if user is currently authenticated.
 *
 * @returns true if user has valid session
 */
export async function isAuthenticated(): Promise<boolean> {
  const result = await getSession();
  return result?.data?.user !== null && result?.data?.user !== undefined;
}
