/**
 * Better Auth API route handler.
 *
 * This catch-all route handles all Better Auth API requests
 * including signin, signup, signout, and session management.
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";
import { NextRequest, NextResponse } from "next/server";

// Use Node.js runtime for database compatibility
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Disable body parser - Better Auth handles it
export const fetchCache = "force-no-store";

// Get handlers from Better Auth
const handlers = toNextJsHandler(auth);

// Wrap with error handling and logging
export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url);
    console.log("[Auth API] GET:", url.pathname);
    console.log("[Auth API] Cookies:", request.cookies.getAll().map(c => c.name).join(", "));

    const response = await handlers.GET(request);

    // Log response status and set-cookie headers for debugging
    console.log("[Auth API] GET Response status:", response.status);
    const setCookieHeaders = response.headers.getSetCookie();
    if (setCookieHeaders.length > 0) {
      console.log("[Auth API] Set-Cookie headers:", setCookieHeaders.length);
    }

    return response;
  } catch (error) {
    console.error("[Auth API] GET error:", error);
    return NextResponse.json(
      { error: "Internal server error", details: String(error) },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const url = new URL(request.url);
    console.log("[Auth API] POST:", url.pathname);

    // Clone and log body for debugging (only in non-production)
    if (process.env.NODE_ENV !== "production") {
      const clonedRequest = request.clone();
      const body = await clonedRequest.text();
      // Don't log passwords - just log presence of body
      console.log("[Auth API] POST body length:", body.length);
    }

    const response = await handlers.POST(request);

    // Log response for debugging
    console.log("[Auth API] POST Response status:", response.status);
    const setCookieHeaders = response.headers.getSetCookie();
    if (setCookieHeaders.length > 0) {
      console.log("[Auth API] Set-Cookie headers count:", setCookieHeaders.length);
    }

    return response;
  } catch (error) {
    console.error("[Auth API] POST error:", error);
    return NextResponse.json(
      { error: "Internal server error", details: String(error) },
      { status: 500 }
    );
  }
}
