import { cookies } from "next/headers";

const SESSION_COOKIE = "app_session";

export type AppSession = {
  id: number;
  username: string;
};

export async function getSession(): Promise<AppSession | null> {
  const cookieStore = await cookies();
  const raw = cookieStore.get(SESSION_COOKIE)?.value;

  if (!raw) {
    return null;
  }

  try {
    const session = JSON.parse(raw) as AppSession;

    if (
      typeof session.id !== "number" ||
      typeof session.username !== "string" ||
      !session.username
    ) {
      return null;
    }

    return session;
  } catch {
    return null;
  }
}

export async function setSession(session: AppSession): Promise<void> {
  const cookieStore = await cookies();

  cookieStore.set(SESSION_COOKIE, JSON.stringify(session), {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });
}

export async function clearSession(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete(SESSION_COOKIE);
}

export function getSessionFromRequest(
  request: { cookies: { get: (name: string) => { value: string } | undefined } },
): AppSession | null {
  const raw = request.cookies.get(SESSION_COOKIE)?.value;

  if (!raw) {
    return null;
  }

  try {
    const session = JSON.parse(raw) as AppSession;

    if (
      typeof session.id !== "number" ||
      typeof session.username !== "string" ||
      !session.username
    ) {
      return null;
    }

    return session;
  } catch {
    return null;
  }
}
