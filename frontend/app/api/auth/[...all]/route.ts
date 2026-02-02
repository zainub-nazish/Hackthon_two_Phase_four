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

// Get handlers from Better Auth
const handlers = toNextJsHandler(auth);

// Wrap with error handling
export async function GET(request: NextRequest) {
  try {
    console.log("[Auth API] GET request:", request.url);
    return await handlers.GET(request);
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
    console.log("[Auth API] POST request:", request.url);
    const clonedRequest = request.clone();
    const body = await clonedRequest.text();
    console.log("[Auth API] POST body:", body);
    return await handlers.POST(request);
  } catch (error) {
    console.error("[Auth API] POST error:", error);
    return NextResponse.json(
      { error: "Internal server error", details: String(error) },
      { status: 500 }
    );
  }
}
