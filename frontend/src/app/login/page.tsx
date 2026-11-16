import { Suspense } from "react";
import type { Metadata } from "next";

import { LoginForm } from "@/components/auth/LoginForm";

export const metadata: Metadata = {
  title: "Sign In — Enterprise AI Assistant",
  description: "Secure enterprise gateway for Enterprise AI Assistant. Access reasoning models, connected knowledge, and autonomous agents.",
};

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen w-full flex flex-col items-center justify-center bg-slate-950 text-slate-300">
          <div className="flex flex-col items-center space-y-4">
            <div className="h-10 w-10 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
            <p className="text-sm font-medium tracking-wide text-slate-400 animate-pulse">
              Initializing Enterprise Security Enclave...
            </p>
          </div>
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
