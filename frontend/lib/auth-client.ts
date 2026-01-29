/**
 * Better Auth client-side helper.
 *
 * Provides client-side authentication utilities for React components.
 * Build: 2026-01-29-v4 - Lazy initialization with window.location.origin
 */

import { createAuthClient } from "better-auth/react";

// Lazy-initialized auth client - only created on first use
let _authClient: ReturnType<typeof createAuthClient> | null = null;

function getAuthClient() {
  if (!_authClient) {
    // Create client with current window origin (only runs in browser)
    const baseURL = typeof window !== "undefined"
      ? window.location.origin
      : "https://frontend-delta-two-31.vercel.app";

    console.log("[Auth] Creating client with baseURL:", baseURL);
    _authClient = createAuthClient({ baseURL });
  }
  return _authClient;
}

// Wrapper functions that lazily initialize the client
export const signIn = {
  email: async (data: { email: string; password: string }) => {
    return getAuthClient().signIn.email(data);
  },
};

export const signUp = {
  email: async (data: { email: string; password: string; name: string }) => {
    return getAuthClient().signUp.email(data);
  },
};

export const signOut = async () => {
  return getAuthClient().signOut();
};

export const useSession = () => {
  return getAuthClient().useSession();
};

export const getSession = async () => {
  return getAuthClient().getSession();
};

// Export the getter for direct access if needed
export { getAuthClient as authClient };

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
