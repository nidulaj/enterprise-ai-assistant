"use server";

import { redirect } from "next/navigation";

import { clearSession, setSession } from "@/lib/auth/session";
import { verifyCredentials } from "@/lib/auth/verify-credentials";

export async function login(
  username: string,
  password: string,
): Promise<{ error: string } | { success: true }> {
  const session = await verifyCredentials(username, password);

  if (!session) {
    return { error: "Invalid username or password." };
  }

  await setSession(session);
  return { success: true };
}

export async function signOut(): Promise<void> {
  await clearSession();
  redirect("/login");
}
