# Quickstart: Frontend Application

**Feature**: 003-frontend-app
**Estimated Setup Time**: 20 minutes

## Prerequisites

- Node.js 20+ installed
- Backend API running (feature 002-backend-api-data-layer)
- Better Auth configured on backend (feature 001-jwt-auth)

## Step 1: Create Next.js Application

```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"
```

Select options:
- TypeScript: Yes
- ESLint: Yes
- Tailwind CSS: Yes
- `src/` directory: No (use app/ directly)
- App Router: Yes
- Import alias: @/*

## Step 2: Install Dependencies

```bash
npm install clsx tailwind-merge
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

## Step 3: Configure Environment

Create `frontend/.env.local`:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Better Auth (if using Better Auth client)
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

## Step 4: Create API Client

Create `frontend/lib/api/client.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined'
    ? localStorage.getItem('auth_token')
    : null;

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Handle unauthorized - redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    const error = await response.json();
    throw new Error(error.detail || 'API request failed');
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}
```

## Step 5: Create Auth Context

Create `frontend/lib/auth/context.tsx`:

```typescript
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const storedToken = localStorage.getItem('auth_token');
    const storedUser = localStorage.getItem('auth_user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = (newToken: string, newUser: User) => {
    localStorage.setItem('auth_token', newToken);
    localStorage.setItem('auth_user', JSON.stringify(newUser));
    setToken(newToken);
    setUser(newUser);
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      isAuthenticated: !!token,
      isLoading,
      login,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

## Step 6: Create Root Layout

Update `frontend/app/layout.tsx`:

```typescript
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/lib/auth/context';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Todo App',
  description: 'A professional multi-user todo application',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

## Step 7: Create Basic Page Structure

Create `frontend/app/page.tsx`:

```typescript
'use client';

import { useAuth } from '@/lib/auth/context';
import { redirect } from 'next/navigation';
import { useEffect } from 'react';

export default function Home() {
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        redirect('/dashboard');
      } else {
        redirect('/login');
      }
    }
  }, [isAuthenticated, isLoading]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
    </div>
  );
}
```

## Step 8: Run Development Server

```bash
npm run dev
```

Open http://localhost:3000 to see the application.

## Verification Checklist

- [ ] Next.js app created with App Router
- [ ] Tailwind CSS configured and working
- [ ] API client can reach backend
- [ ] Auth context provides user state
- [ ] Environment variables configured
- [ ] Root layout includes AuthProvider

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement login page with Better Auth
3. Build task dashboard with CRUD operations
4. Add responsive styling
5. Implement loading and error states

## Troubleshooting

### CORS Errors
- Ensure backend has CORS configured for frontend origin
- Check `NEXT_PUBLIC_API_BASE_URL` matches backend URL

### Auth Token Not Found
- Verify token is stored after login
- Check localStorage in browser DevTools

### TypeScript Errors
- Run `npm run type-check` to see all errors
- Ensure types match API contract
