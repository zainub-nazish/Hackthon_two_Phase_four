/**
 * Better Auth client-side helper.
 *
 * Provides client-side authentication utilities for React components.
 */

import { createAuthClient } from "better-auth/client";

// Create auth client instance
// Use NEXT_PUBLIC_ prefix for client-side access
// In browser, if NEXT_PUBLIC_APP_URL is not set, use window.location.origin
const getBaseURL = () => {
  if (process.env.NEXT_PUBLIC_APP_URL) {
    return process.env.NEXT_PUBLIC_APP_URL;
  }
  // In browser, use current origin
  if (typeof window !== "undefined") {
    return window.location.origin;
  }
  // Fallback for server-side
  return "";
};

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
