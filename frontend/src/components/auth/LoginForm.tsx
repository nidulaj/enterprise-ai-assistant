"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState, KeyboardEvent } from "react";
import { 
  User, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  Loader2, 
  X, 
  HelpCircle, 
  KeyRound, 
  AlertTriangle, 
  Check, 
  Info,
  Shield
} from "lucide-react";

import { login } from "@/app/login/actions";
import { AuthCard, AuthError } from "@/components/auth/AuthCard";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") ?? "/dashboard";
  const callbackError = searchParams.get("error");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isCapsLockOn, setIsCapsLockOn] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);
  const [showDemoHelper, setShowDemoHelper] = useState(false);

  const [error, setError] = useState<string | null>(
    callbackError === "auth_callback_failed"
      ? "Authentication session timed out or failed. Please sign in again."
      : null,
  );
  const [loading, setLoading] = useState(false);

  const handleKeyDownOrUp = (event: KeyboardEvent<HTMLInputElement>) => {
    setIsCapsLockOn(event.getModifierState("CapsLock"));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    const result = await login(username, password);

    setLoading(false);

    if ("error" in result) {
      setError(result.error);
      return;
    }

    router.push(nextPath);
    router.refresh();
  };

  const handleFillDemo = (demoUser: string, demoPass: string) => {
    setUsername(demoUser);
    setPassword(demoPass);
    setError(null);
  };

  return (
    <>
      <AuthCard
        title="Sign in to Workspace"
        description="Provide your organization username and security credentials."
      >
        <form className="space-y-4 sm:space-y-5" onSubmit={handleSubmit}>
          <AuthError message={error} />

          {/* Username Input Field */}
          <div className="space-y-1.5">
            <label
              htmlFor="username"
              className="block text-xs font-medium text-slate-300"
            >
              Enterprise Username
            </label>
            <div className="relative group">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                <User className="h-4 w-4" />
              </div>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                autoFocus
                required
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="e.g. admin or employee ID"
                className="w-full rounded-xl border border-slate-700/80 bg-slate-950/70 pl-10 pr-9 py-2.5 text-sm text-slate-100 placeholder-slate-500 shadow-inner outline-none transition-all duration-200 focus:border-indigo-500 focus:bg-slate-950 focus:ring-2 focus:ring-indigo-500/20"
              />
              {username.length > 0 && (
                <button
                  type="button"
                  onClick={() => setUsername("")}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-500 hover:text-slate-300 transition-colors"
                  aria-label="Clear username"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>

          {/* Password Input Field */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label
                htmlFor="password"
                className="block text-xs font-medium text-slate-300"
              >
                Password
              </label>
              <button
                type="button"
                onClick={() => setShowHelpModal(true)}
                className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium flex items-center gap-1"
              >
                <HelpCircle className="h-3 w-3" />
                Forgot password?
              </button>
            </div>
            
            <div className="relative group">
              <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-500 group-focus-within:text-indigo-400 transition-colors">
                <Lock className="h-4 w-4" />
              </div>
              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete="current-password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                onKeyDown={handleKeyDownOrUp}
                onKeyUp={handleKeyDownOrUp}
                placeholder="Enter your account password"
                className="w-full rounded-xl border border-slate-700/80 bg-slate-950/70 pl-10 pr-10 py-2.5 text-sm text-slate-100 placeholder-slate-500 shadow-inner outline-none transition-all duration-200 focus:border-indigo-500 focus:bg-slate-950 focus:ring-2 focus:ring-indigo-500/20"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-500 hover:text-slate-300 transition-colors focus:outline-none"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>

            {/* Caps Lock Indicator */}
            {isCapsLockOn && (
              <div className="flex items-center gap-1.5 text-[11px] text-amber-400 font-medium pt-1 animate-fadeIn">
                <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                <span>Caps Lock is ON</span>
              </div>
            )}
          </div>

          {/* Remember Me & Quick Helper Options */}
          <div className="flex items-center justify-between pt-0.5">
            <label className="flex items-center gap-2 cursor-pointer select-none">
              <div className="relative">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="sr-only"
                />
                <div
                  className={`h-4 w-4 rounded border transition-colors flex items-center justify-center ${
                    rememberMe
                      ? "border-indigo-500 bg-indigo-600 text-white"
                      : "border-slate-700 bg-slate-950/80 hover:border-slate-600"
                  }`}
                >
                  {rememberMe && <Check className="h-3 w-3 stroke-[2.5]" />}
                </div>
              </div>
              <span className="text-xs text-slate-400">Remember this device</span>
            </label>

            <button
              type="button"
              onClick={() => setShowDemoHelper(!showDemoHelper)}
              className="text-xs text-slate-400 hover:text-indigo-300 transition-colors inline-flex items-center gap-1"
            >
              <Info className="h-3 w-3" />
              <span>{showDemoHelper ? "Hide info" : "Access note"}</span>
            </button>
          </div>

          {/* Collapsible Demo/Access Helper Pill */}
          {showDemoHelper && (
            <div className="rounded-xl border border-indigo-500/20 bg-indigo-950/30 p-3 text-xs text-slate-300 space-y-2 animate-fadeIn">
              <div className="flex items-start gap-2">
                <KeyRound className="h-4 w-4 text-indigo-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="font-medium text-indigo-200">Database Authentication</p>
                  <p className="text-slate-400 text-[11px] leading-relaxed">
                    Credentials verify directly against the local PostgreSQL / Supabase users table.
                  </p>
                </div>
              </div>
              <div className="pt-1 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => handleFillDemo("admin", "admin123")}
                  className="rounded-lg bg-indigo-600/30 border border-indigo-500/40 px-2.5 py-1 text-[11px] font-medium text-indigo-200 hover:bg-indigo-600/50 transition-colors"
                >
                  Prefill Admin demo
                </button>
              </div>
            </div>
          )}

          {/* Submit Action Button */}
          <button
            type="submit"
            disabled={loading}
            className="group relative w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 via-indigo-600 to-violet-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-600/25 transition-all duration-200 hover:from-indigo-400 hover:via-indigo-500 hover:to-violet-500 hover:shadow-indigo-500/35 active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-white" />
                <span>Authenticating Enclave...</span>
              </>
            ) : (
              <>
                <span>Sign in to Workspace</span>
                <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
              </>
            )}
          </button>
        </form>
      </AuthCard>

      {/* IT Support / Password Reset Modal */}
      {showHelpModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl text-slate-100 ring-1 ring-white/10">
            <div className="flex items-start justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  <Shield className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="font-semibold text-base text-white">Enterprise Access Support</h3>
                  <p className="text-xs text-slate-400">Account Recovery & Credential Policies</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowHelpModal(false)}
                className="text-slate-400 hover:text-white rounded-lg p-1 hover:bg-slate-800 transition-colors"
                aria-label="Close modal"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="py-4 space-y-3.5 text-xs text-slate-300">
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                <p className="font-medium text-indigo-300">Self-Service Reset</p>
                <p className="text-slate-400 leading-relaxed">
                  If your enterprise identity is bound to Active Directory or SSO, resets are handled via your corporate Identity Provider portal.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1">
                <p className="font-medium text-indigo-300">Database & Local Users</p>
                <p className="text-slate-400 leading-relaxed">
                  For standalone accounts in the database <code className="text-indigo-300 bg-slate-800 px-1 py-0.5 rounded">users</code> table, contact your workspace administrator to reset your hash.
                </p>
              </div>

              <div className="rounded-xl border border-indigo-500/20 bg-indigo-950/20 p-3 flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-200">IT Help Desk</p>
                  <p className="text-[11px] text-slate-400">support@enterprise-ai.internal</p>
                </div>
                <span className="inline-flex items-center gap-1 text-[11px] text-indigo-400 font-medium">
                  Internal SLA &lt;15m
                </span>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="button"
                onClick={() => setShowHelpModal(false)}
                className="rounded-xl bg-slate-800 hover:bg-slate-700 px-4 py-2 text-xs font-semibold text-white transition-colors"
              >
                Close Support
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
