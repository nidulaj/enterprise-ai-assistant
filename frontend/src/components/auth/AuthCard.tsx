"use client";

import type { ReactNode } from "react";
import { 
  Bot, 
  Sparkles, 
  ShieldCheck, 
  Cpu, 
  Zap, 
  Lock, 
  AlertCircle,
  Server,
  Network,
  Database,
  CheckSquare,
  Calendar,
  Mail
} from "lucide-react";

type AuthCardProps = {
  title: string;
  description: string;
  children: ReactNode;
};

export function AuthCard({ title, description, children }: AuthCardProps) {
  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-slate-950 text-slate-100 overflow-x-hidden p-4 sm:p-6 lg:p-8">
      {/* Background Decorative Mesh & Glows */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Subtle grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#33415515_1px,transparent_1px),linear-gradient(to_bottom,#33415515_1px,transparent_1px)] bg-[size:3.5rem_3.5rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-70" />

        {/* Ambient colored orbs */}
        <div className="absolute -top-40 -left-40 h-[520px] w-[520px] rounded-full bg-indigo-600/15 blur-[120px]" />
        <div className="absolute top-1/2 -right-40 h-[520px] w-[520px] rounded-full bg-violet-600/15 blur-[140px]" />
        <div className="absolute -bottom-40 left-1/3 h-[460px] w-[460px] rounded-full bg-blue-600/10 blur-[130px]" />
      </div>

      <div className="relative z-10 w-full max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          
          {/* Left Column: Enterprise AI Branding & Feature Highlights */}
          <div className="lg:col-span-6 xl:col-span-7 flex flex-col justify-center space-y-8 py-4 sm:py-6 lg:py-0">
            {/* Top Brand Pill */}
            <div className="inline-flex items-center gap-2.5 self-start rounded-full border border-indigo-500/30 bg-indigo-500/10 px-4 py-1.5 text-xs font-medium text-indigo-300 backdrop-blur-md shadow-sm">
              <span className="flex h-2 w-2 rounded-full bg-indigo-400 animate-pulse" />
              <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
              <span>Enterprise AI Platform</span>
              <span className="text-indigo-400/50">|</span>
              <span className="text-slate-400">v2.4 Private Cloud</span>
            </div>

            {/* Brand Title & Headline */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-600 shadow-xl shadow-indigo-500/25 ring-1 ring-white/20">
                  <Bot className="h-7 w-7 text-white" />
                </div>
                <div>
                  <h2 className="text-sm font-semibold tracking-wider uppercase text-indigo-400">
                    Enterprise AI Assistant
                  </h2>
                  <p className="text-xs text-slate-400">Autonomous Intelligence & Private Knowledge</p>
                </div>
              </div>

              <h1 className="text-3xl sm:text-4xl xl:text-5xl font-extrabold tracking-tight text-white leading-[1.15]">
                Intelligent Reasoning for the Modern Enterprise.
              </h1>

              <p className="text-base sm:text-lg text-slate-400 max-w-xl leading-relaxed">
                Connect your organization&apos;s confidential data, orchestrate advanced models, and accelerate decision-making inside a zero-trust enclave.
              </p>
            </div>

            {/* Orchestrated Multi-Agent Cluster Showcase */}
            <div className="rounded-2xl border border-indigo-500/20 bg-indigo-950/20 p-3.5 backdrop-blur-sm space-y-2.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-indigo-300 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
                  <Network className="h-3.5 w-3.5 text-indigo-400" />
                  Autonomous Multi-Agent Swarm
                </span>
                <span className="text-[10px] text-emerald-400 font-medium flex items-center gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  LangGraph Active
                </span>
              </div>
              <div className="flex flex-wrap gap-2 text-xs">
                <div className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700/60 bg-slate-900/60 px-2.5 py-1 text-slate-300 hover:border-cyan-500/40 transition-colors">
                  <Database className="h-3 w-3 text-cyan-400" />
                  <span>Knowledge RAG Agent</span>
                </div>
                <div className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700/60 bg-slate-900/60 px-2.5 py-1 text-slate-300 hover:border-purple-500/40 transition-colors">
                  <CheckSquare className="h-3 w-3 text-purple-400" />
                  <span>ClickUp Tasks Agent</span>
                </div>
                <div className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700/60 bg-slate-900/60 px-2.5 py-1 text-slate-300 hover:border-blue-500/40 transition-colors">
                  <Calendar className="h-3 w-3 text-blue-400" />
                  <span>Calendar Agent</span>
                </div>
                <div className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700/60 bg-slate-900/60 px-2.5 py-1 text-slate-300 hover:border-amber-500/40 transition-colors">
                  <Mail className="h-3 w-3 text-amber-400" />
                  <span>SMTP Email Agent</span>
                </div>
              </div>
            </div>

            {/* Value Proposition Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 pt-2">
              <div className="group rounded-2xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm transition-all duration-300 hover:border-indigo-500/40 hover:bg-slate-900/70 hover:shadow-lg hover:shadow-indigo-500/5">
                <div className="mb-2.5 flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 group-hover:scale-110 transition-transform">
                  <Cpu className="h-5 w-5" />
                </div>
                <h3 className="text-sm font-semibold text-slate-200">Neural RAG</h3>
                <p className="mt-1 text-xs text-slate-400 leading-snug">
                  Real-time private document indexing with verifiable citations.
                </p>
              </div>

              <div className="group rounded-2xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm transition-all duration-300 hover:border-violet-500/40 hover:bg-slate-900/70 hover:shadow-lg hover:shadow-violet-500/5">
                <div className="mb-2.5 flex h-9 w-9 items-center justify-center rounded-xl bg-violet-500/10 text-violet-400 border border-violet-500/20 group-hover:scale-110 transition-transform">
                  <Zap className="h-5 w-5" />
                </div>
                <h3 className="text-sm font-semibold text-slate-200">Multi-Model</h3>
                <p className="mt-1 text-xs text-slate-400 leading-snug">
                  Dynamic routing between frontier LLMs and domain fine-tunes.
                </p>
              </div>

              <div className="group rounded-2xl border border-slate-800/80 bg-slate-900/40 p-4 backdrop-blur-sm transition-all duration-300 hover:border-emerald-500/40 hover:bg-slate-900/70 hover:shadow-lg hover:shadow-emerald-500/5">
                <div className="mb-2.5 flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 group-hover:scale-110 transition-transform">
                  <ShieldCheck className="h-5 w-5" />
                </div>
                <h3 className="text-sm font-semibold text-slate-200">Zero Retention</h3>
                <p className="mt-1 text-xs text-slate-400 leading-snug">
                  Strict tenant isolation with full audit trail compliance.
                </p>
              </div>
            </div>

            {/* Bottom System Status & Compliance */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-800/60 text-xs text-slate-400">
              <div className="flex items-center gap-2">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
                </span>
                <span className="font-medium text-slate-300">All Neural Services Operational</span>
                <span className="text-slate-600">·</span>
                <span>99.99% SLA</span>
              </div>

              <div className="flex items-center gap-3 text-slate-500">
                <span className="hover:text-slate-400 transition-colors">SOC 2 Type II</span>
                <span>•</span>
                <span className="hover:text-slate-400 transition-colors">ISO 27001</span>
                <span>•</span>
                <span className="hover:text-slate-400 transition-colors">TLS 1.3</span>
              </div>
            </div>
          </div>

          {/* Right Column: The Authentication Card */}
          <div className="lg:col-span-6 xl:col-span-5 w-full max-w-md mx-auto">
            <div className="relative rounded-3xl border border-slate-800/90 bg-slate-900/80 p-6 sm:p-8 shadow-2xl backdrop-blur-xl ring-1 ring-white/10 before:absolute before:inset-x-0 before:top-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-indigo-500/60 before:to-transparent">
              
              {/* Card Header */}
              <div className="mb-6 space-y-1.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      <Lock className="h-4 w-4" />
                    </div>
                    <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
                      Secure Portal
                    </span>
                  </div>
                  <span className="inline-flex items-center gap-1 rounded-md bg-slate-800/80 px-2 py-0.5 text-[11px] font-medium text-slate-400 border border-slate-700/50">
                    <Server className="h-3 w-3 text-emerald-400" />
                    Production
                  </span>
                </div>

                <h2 className="text-2xl font-bold tracking-tight text-white pt-2">{title}</h2>
                <p className="text-sm text-slate-400">{description}</p>
              </div>

              {/* Form Content */}
              {children}

              {/* Card Footer Security Assurance */}
              <div className="mt-6 pt-5 border-t border-slate-800/80 flex items-center justify-center gap-2 text-center text-xs text-slate-400">
                <ShieldCheck className="h-4 w-4 text-indigo-400 shrink-0" />
                <span>Protected by 256-bit TLS encrypted session & active audit logging</span>
              </div>
            </div>

            {/* Quick footer links */}
            <div className="mt-4 flex items-center justify-center gap-4 text-xs text-slate-500">
              <span className="hover:text-slate-400 cursor-pointer transition-colors">Privacy Policy</span>
              <span>•</span>
              <span className="hover:text-slate-400 cursor-pointer transition-colors">Security Enclave</span>
              <span>•</span>
              <span className="hover:text-slate-400 cursor-pointer transition-colors">System Status</span>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

export function AuthError({ message }: { message: string | null }) {
  if (!message) {
    return null;
  }

  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-3.5 text-sm text-red-200 backdrop-blur-sm animate-fadeIn"
    >
      <AlertCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
      <div className="space-y-0.5">
        <p className="font-semibold text-red-300">Authentication Error</p>
        <p className="text-xs text-red-200/90 leading-relaxed">{message}</p>
      </div>
    </div>
  );
}
