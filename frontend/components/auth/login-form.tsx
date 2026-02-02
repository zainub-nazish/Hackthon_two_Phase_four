"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signIn } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      console.log("Attempting login for:", email);

      const result = await signIn.email({
        email,
        password,
      });

      console.log("Login result:", JSON.stringify(result, null, 2));

      if (result.error) {
        console.error("Login error from server:", result.error);
        setError(result.error.message || result.error.code || "Invalid email or password");
        return;
      }

      // Redirect to dashboard on success
      router.push("/tasks");
    } catch (err) {
      // Log full error for debugging
      console.error("Login error details:", err);
      console.error("Error type:", typeof err);
      console.error("Error JSON:", JSON.stringify(err, null, 2));

      // Show actual error message for debugging
      if (err instanceof Error) {
        setError(`Error: ${err.message}`);
      } else if (typeof err === 'object' && err !== null) {
        setError(`Error: ${JSON.stringify(err)}`);
      } else {
        setError(`Error: ${String(err)}`);
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sign in</CardTitle>
        <CardDescription>
          Enter your email and password to access your tasks
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div
              className="rounded-md bg-danger/20 border border-danger/30 p-3 text-sm text-danger"
              role="alert"
            >
              {error}
            </div>
          )}

          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            autoComplete="email"
            disabled={isLoading}
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
            autoComplete="current-password"
            disabled={isLoading}
          />

          <Button
            type="submit"
            className="w-full"
            isLoading={isLoading}
          >
            Sign in
          </Button>

          <p className="text-center text-sm text-muted">
            Don&apos;t have an account?{" "}
            <Link
              href="/signup"
              className="font-medium text-primary hover:text-primary-hover"
            >
              Sign up
            </Link>
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
