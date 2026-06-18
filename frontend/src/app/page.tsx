import Link from "next/link";

import { SignOutButton } from "@/components/auth/SignOutButton";
import { getSession } from "@/lib/auth/session";

export default async function HomePage() {
  const session = await getSession();
  const displayName = session?.username ?? "User";

  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4 py-16 text-center">
      <p className="text-sm font-medium uppercase tracking-wide text-indigo-600">
        Enterprise AI Assistant
      </p>
      <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl">
        Sign in to continue
      </h1>
      <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">
        Sign in with your username and password from the users table. Your
        session is stored in a secure cookie.
      </p>

      {session ? (
        <div className="mt-10 space-y-4">
          <p className="text-sm text-slate-600">
            Signed in as{" "}
            <span className="font-medium text-slate-900">{displayName}</span>
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              href="/dashboard"
              className="rounded-md bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
            >
              Open dashboard
            </Link>
            <SignOutButton className="rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50" />
          </div>
        </div>
      ) : (
        <div className="mt-10">
          <Link
            href="/login"
            className="rounded-md bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500"
          >
            Sign in
          </Link>
        </div>
      )}
    </div>
  );
}
