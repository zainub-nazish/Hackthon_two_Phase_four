"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";

export function UserMenu() {
  const { user, isAuthenticated, isLoading, signOut } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Close menu on escape
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, []);

  if (isLoading) {
    return (
      <div className="h-10 w-10 animate-pulse rounded-full bg-white/10" />
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  const initials = user.email
    ? user.email.charAt(0).toUpperCase()
    : user.name
      ? user.name.charAt(0).toUpperCase()
      : "U";

  return (
    <div className="relative" ref={menuRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/20 text-primary font-medium hover:bg-primary/30 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-dark transition-colors"
        aria-expanded={isOpen}
        aria-haspopup="true"
        aria-label="User menu"
      >
        {initials}
      </button>

      {isOpen && (
        <div
          className="absolute right-0 mt-2 w-56 origin-top-right rounded-md bg-surface border border-white/10 shadow-lg focus:outline-none animate-fade-in"
          role="menu"
          aria-orientation="vertical"
        >
          <div className="px-4 py-3 border-b border-white/10">
            <p className="text-sm font-medium text-light">
              {user.name || "User"}
            </p>
            <p className="text-sm text-muted truncate">{user.email}</p>
          </div>
          <div className="py-1">
            <Button
              variant="ghost"
              className="w-full justify-start px-4 py-2 text-sm text-light hover:bg-white/5 rounded-none"
              onClick={async () => {
                setIsOpen(false);
                await signOut();
              }}
              role="menuitem"
            >
              <svg
                className="mr-2 h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              Sign out
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
