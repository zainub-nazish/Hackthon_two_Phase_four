/**
 * Better Auth client-side helper.
 *
 * Provides client-side authentication utilities for React components.
 * Build: 2026-02-02-v9 - Lazy initialization for correct URL
 */

import { createAuthClient } from "better-auth/react";

// Lazy-initialized auth client
let _authClient: ReturnType<typeof createAuthClient> | null = null;

function getAuthClient() {
  if (!_authClient) {
    // Get the correct base URL
    const baseURL = typeof window !== "undefined"
      ? window.location.origin
      : "https://frontend-delta-two-31.vercel.app";

    console.log("[Auth Client] Initializing with baseURL:", baseURL);

    _authClient = createAuthClient({ baseURL });
  }
  return _authClient;
}

// Export auth client getter
export const authClient = {
  get signIn() { return getAuthClient().signIn; },
  get signUp() { return getAuthClient().signUp; },
  get signOut() { return getAuthClient().signOut; },
  get useSession() { return getAuthClient().useSession; },
  get getSession() { return getAuthClient().getSession; },
};

// Re-export commonly used methods as functions
export const signIn = {
  get email() { return getAuthClient().signIn.email; },
};
export const signUp = {
  get email() { return getAuthClient().signUp.email; },
};
export const signOut = () => getAuthClient().signOut();
export const useSession = () => getAuthClient().useSession();
export const getSession = () => getAuthClient().getSession();

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
