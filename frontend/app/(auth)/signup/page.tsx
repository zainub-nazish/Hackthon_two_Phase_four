import type { Metadata } from "next";
import { SignupForm } from "@/components/auth/signup-form";

export const metadata: Metadata = {
  title: "Sign Up - Todo App",
  description: "Create your Todo App account",
};

export default function SignupPage() {
  return <SignupForm />;
}
