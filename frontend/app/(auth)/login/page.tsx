import type { Metadata } from "next";
import { LoginForm } from "@/components/auth/login-form";

export const metadata: Metadata = {
  title: "Sign In - Todo App",
  description: "Sign in to your Todo App account",
};

export default function LoginPage() {
  return <LoginForm />;
}
