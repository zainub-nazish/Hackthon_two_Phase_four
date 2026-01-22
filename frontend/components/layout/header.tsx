"use client";

import Link from "next/link";
import { UserMenu } from "./user-menu";
import { MobileNav, DesktopNav } from "./nav";

export function Header() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/10 bg-surface">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-4 md:gap-6">
          <MobileNav />
          <Link href="/" className="flex items-center gap-2">
            <svg
              className="h-8 w-8 text-primary"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
              />
            </svg>
            <span className="text-xl font-bold text-light hidden sm:inline">Task Management</span>
            <span className="text-xl font-bold text-light sm:hidden">Tasks</span>
          </Link>
          <DesktopNav />
        </div>
        <UserMenu />
      </div>
    </header>
  );
}
