import Link from "next/link";
import { redirect } from "next/navigation";

import { SignOutButton } from "@/components/auth/SignOutButton";
import { getSession } from "@/lib/auth/session";

export default async function DashboardPage() {
  const session = await getSession();

  if (!session) {
    redirect("/login?next=/dashboard");
  }

  const displayName = session.username;

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-3xl flex-col justify-center px-4 py-12">
      <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-wide text-indigo-600">
          Signed in
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-900">Dashboard</h1>
        <p className="mt-3 text-slate-600">
          You are signed in as{" "}
          <span className="font-medium text-slate-900">{displayName}</span>.
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/"
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Back home
          </Link>
          <SignOutButton className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700" />
        </div>
      </div>
    </div>
  );
}
