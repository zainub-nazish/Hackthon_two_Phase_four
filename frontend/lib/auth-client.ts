/**
 * Better Auth client-side helper.
 *
 * Provides client-side authentication utilities for React components.
 * Build: 2026-01-31-v6 - Auto-detect URL
 */

import { createAuthClient } from "better-auth/react";

// Auto-detect the base URL
// In browser: use current origin (works for both localhost and Vercel)
// In server: use NEXT_PUBLIC_APP_URL or fallback to production URL
function getBaseURL(): string {
  if (typeof window !== "undefined") {
    // Client-side: use current origin
    return window.location.origin;
  }
  // Server-side: use env variable or production URL
  return process.env.NEXT_PUBLIC_APP_URL || "https://frontend-delta-two-31.vercel.app";
}

// Create auth client with auto-detected URL
export const authClient = createAuthClient({
  baseURL: getBaseURL(),
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
