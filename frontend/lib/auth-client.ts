/**
 * Better Auth client-side helper.
 *
 * Provides client-side authentication utilities for React components.
 * Uses relative URLs for API calls to work across all environments.
 */

import { createAuthClient } from "better-auth/react";

// Create auth client with relative URLs (no baseURL needed)
// This ensures API calls like /api/auth/sign-up work on any domain
export const authClient = createAuthClient();

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
