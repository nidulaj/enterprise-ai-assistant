import { Suspense } from "react";

import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <Suspense
      fallback={<div className="p-10 text-center text-slate-600">Loading...</div>}
    >
      <LoginForm />
    </Suspense>
  );
}
