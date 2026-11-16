import { Suspense } from "react";
import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { getSession } from "@/lib/auth/session";
import { LoginForm } from "@/components/auth/LoginForm";

export const metadata: Metadata = {
  title: "Enterprise AI Assistant — Multi-Agent Intelligence Platform",
  description:
    "Connect confidential data, orchestrate autonomous multi-agent reasoning, and accelerate decision-making inside a zero-trust enclave.",
};

export default async function HomePage() {
  // If already authenticated with a valid JWT session, navigate straight to the chat assistant
  const session = await getSession();

  if (session) {
    redirect("/chat");
  }

  return (
    <Suspense
      fallback={
        <div className="min-h-screen w-full flex flex-col items-center justify-center bg-slate-950 text-slate-300">
          <div className="flex flex-col items-center space-y-4">
            <div className="h-10 w-10 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
            <p className="text-sm font-medium tracking-wide text-slate-400 animate-pulse">
              Initializing Enterprise Multi-Agent Enclave...
            </p>
          </div>
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
