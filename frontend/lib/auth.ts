/**
 * Better Auth server configuration.
 *
 * This configures Better Auth with Neon PostgreSQL database.
 */

import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { drizzle } from "drizzle-orm/neon-http";
import { neon } from "@neondatabase/serverless";
import * as schema from "../auth-schema";

// Debug: Log environment variables (without exposing secrets)
console.log("[Auth Config] DATABASE_URL exists:", !!process.env.DATABASE_URL);
console.log("[Auth Config] BETTER_AUTH_SECRET exists:", !!process.env.BETTER_AUTH_SECRET);
console.log("[Auth Config] NEXT_PUBLIC_APP_URL:", process.env.NEXT_PUBLIC_APP_URL);

// Validate required environment variables
if (!process.env.DATABASE_URL) {
  console.error("[Auth Config] ERROR: DATABASE_URL is not set!");
}
if (!process.env.BETTER_AUTH_SECRET) {
  console.error("[Auth Config] ERROR: BETTER_AUTH_SECRET is not set!");
}

// Create Neon database connection
const sql = neon(process.env.DATABASE_URL || "");
const db = drizzle(sql, { schema });

// Determine if running in production (Vercel)
const isProduction = process.env.NODE_ENV === "production" || process.env.VERCEL === "1";

export const auth = betterAuth({
  // Use environment variable for shared secret
  secret: process.env.BETTER_AUTH_SECRET,

  // Base URL for auth endpoints (required for Vercel)
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "https://frontend-delta-two-31.vercel.app",

  // Database configuration - Neon PostgreSQL
  database: drizzleAdapter(db, {
    provider: "pg",
    schema,
  }),

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session after 1 day
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes cache
    },
  },

  // Advanced cookie configuration for Vercel/HTTPS
  advanced: {
    cookiePrefix: "better-auth",
    useSecureCookies: isProduction, // Secure cookies on HTTPS
    crossSubDomainCookies: {
      enabled: false, // Disable unless using subdomains
    },
  },

  // Trusted origins for CORS
  trustedOrigins: [
    "http://localhost:3000",
    process.env.NEXT_PUBLIC_APP_URL,
    // VERCEL_URL is automatically set by Vercel (includes preview URLs)
    process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : undefined,
    "https://frontend-delta-two-31.vercel.app",
  ].filter((origin): origin is string => Boolean(origin)),

  // Email/password authentication
  emailAndPassword: {
    enabled: true,
  },
});

export type Auth = typeof auth;
