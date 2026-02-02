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

export const auth = betterAuth({
  // Use environment variable for shared secret
  secret: process.env.BETTER_AUTH_SECRET,

  // Database configuration - Neon PostgreSQL
  database: drizzleAdapter(db, {
    provider: "pg",
    schema,
  }),

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session after 1 day
  },

  // Trusted origins for CORS
  trustedOrigins: [
    "http://localhost:3000",
    process.env.NEXT_PUBLIC_APP_URL,
    // VERCEL_URL is automatically set by Vercel
    process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : undefined,
    "https://frontend-delta-two-31.vercel.app",
  ].filter((origin): origin is string => Boolean(origin)),

  // Email/password authentication
  emailAndPassword: {
    enabled: true,
  },
});

export type Auth = typeof auth;
