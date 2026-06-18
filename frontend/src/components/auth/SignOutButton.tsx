"use client";

import { useTransition } from "react";

import { signOut } from "@/app/login/actions";

type SignOutButtonProps = {
  className?: string;
};

export function SignOutButton({ className }: SignOutButtonProps) {
  const [isPending, startTransition] = useTransition();

  const handleSignOut = () => {
    startTransition(() => {
      void signOut();
    });
  };

  return (
    <button
      type="button"
      onClick={handleSignOut}
      disabled={isPending}
      className={className}
    >
      {isPending ? "Signing out..." : "Sign out"}
    </button>
  );
}
