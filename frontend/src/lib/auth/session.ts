import { cookies } from "next/headers";

export const SESSION_COOKIE = "access_token";

export type AppSession = {
  id: number;
  username: string;
};

const BACKEND_URL =
  process.env.INTERNAL_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:5000";

/**
 * Retrieves the raw access token from the HTTP-only cookie.
 */
export async function getSessionToken(): Promise<string | null> {
  const cookieStore = await cookies();
  return (
    cookieStore.get(SESSION_COOKIE)?.value ||
    cookieStore.get("enterprise_jwt_session")?.value ||
    null
  );
}

/**
 * Validates the session by asking the backend to verify the JWT.
 * The backend handles all cryptographic verification and claims extraction.
 */
export async function getSession(): Promise<AppSession | null> {
  const token = await getSessionToken();

  if (!token) {
    return null;
  }

  try {
    const res = await fetch(`${BACKEND_URL}/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        Cookie: `${SESSION_COOKIE}=${token}`,
      },
      cache: "no-store",
    });

    if (!res.ok) {
      return null;
    }

    const data = await res.json();
    if (!data.authenticated || !data.user) {
      return null;
    }

    return {
      id: data.user.id,
      username: data.user.username,
    };
  } catch (error) {
    console.error("Backend auth verification failed:", error);
    return null;
  }
}

/**
 * Stores the backend-issued JWT token in an HTTP-only secure cookie.
 */
export async function setSessionToken(token: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7, // 7 days
  });
}

/**
 * Clears the active authentication cookie and notifies the backend.
 */
export async function clearSession(): Promise<void> {
  const token = await getSessionToken();
  const cookieStore = await cookies();

  // Clear cookie from browser store
  cookieStore.delete(SESSION_COOKIE);
  cookieStore.delete("enterprise_jwt_session");

  // Notify backend to clear server-side cookie if needed
  try {
    await fetch(`${BACKEND_URL}/auth/logout`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      cache: "no-store",
    });
  } catch {
    // Ignore network issues on logout
  }
}

/**
 * Checks if session token is present on incoming request (used in Next.js middleware).
 */
export function hasSessionInRequest(request: {
  cookies: { get: (name: string) => { value: string } | undefined };
}): boolean {
  const token =
    request.cookies.get(SESSION_COOKIE)?.value ||
    request.cookies.get("enterprise_jwt_session")?.value;
  return Boolean(token && token.length > 10);
}
