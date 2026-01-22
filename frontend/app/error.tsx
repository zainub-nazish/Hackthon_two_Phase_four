"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("Application error:", error);
  }, [error]);

  return (
    <div className="min-h-screen bg-dark flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center">
        {/* Error Icon */}
        <div className="mx-auto w-16 h-16 rounded-full bg-danger/10 flex items-center justify-center mb-6">
          <svg
            className="w-8 h-8 text-danger"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>

        {/* Error Message */}
        <h1 className="text-2xl font-bold text-light mb-2">
          Something went wrong
        </h1>
        <p className="text-muted mb-6">
          We encountered an unexpected error. Please try again or contact support
          if the problem persists.
        </p>

        {/* Error Details (Development only) */}
        {process.env.NODE_ENV === "development" && (
          <div className="mb-6 p-4 rounded-lg bg-surface border border-white/10 text-left">
            <p className="text-xs text-muted font-mono break-all">
              {error.message}
            </p>
            {error.digest && (
              <p className="text-xs text-muted/50 font-mono mt-2">
                Error ID: {error.digest}
              </p>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button
            onClick={reset}
            variant="primary"
            className="min-h-[44px] touch-manipulation"
          >
            Try again
          </Button>
          <Button
            onClick={() => (window.location.href = "/")}
            variant="secondary"
            className="min-h-[44px] touch-manipulation"
          >
            Go to home
          </Button>
        </div>
      </div>
    </div>
  );
}
