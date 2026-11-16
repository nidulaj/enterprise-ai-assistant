"use server";

import { redirect } from "next/navigation";
import {
  clearSession,
  getSession,
  getSessionToken,
  setSessionToken,
} from "@/lib/auth/session";

const BACKEND_URL =
  process.env.INTERNAL_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";

/**
 * Handles user login by delegating credential verification and JWT generation
 * entirely to the Flask backend (/auth/login).
 */
export async function login(
  username: string,
  password: string,
): Promise<{ error: string } | { success: true }> {
  const trimmedUsername = username.trim();

  if (!trimmedUsername || !password) {
    return { error: "Username and password are required." };
  }

  try {
    const res = await fetch(`${BACKEND_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: trimmedUsername,
        password,
      }),
      cache: "no-store",
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok || !data.success || !data.token) {
      return {
        error:
          data.error || "Invalid username or password.",
      };
    }

    // Persist the backend-issued cryptographically signed JWT in HTTP-only cookie
    await setSessionToken(data.token);
    return { success: true };
  } catch (error) {
    console.error("Backend login request failed:", error);
    return {
      error:
        "Unable to reach the authentication server. Please ensure the backend is running.",
    };
  }
}

export async function signOut(): Promise<void> {
  await clearSession();
  redirect("/");
}

export async function getCurrentUserSession() {
  return await getSession();
}

export async function getAuthToken(): Promise<string | null> {
  return await getSessionToken();
}
