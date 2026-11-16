import { NextResponse, type NextRequest } from "next/server";
import { hasSessionInRequest } from "@/lib/auth/session";

export async function updateSession(request: NextRequest) {
  const isAuthenticated = hasSessionInRequest(request);
  const pathname = request.nextUrl.pathname;
  const isAuthRoute = pathname.startsWith("/login");
  const isRoot = pathname === "/";
  const isProtectedRoute = pathname.startsWith("/chat") || pathname.startsWith("/dashboard");

  // 1. Authenticated users visiting root '/' or '/login' -> redirect to '/chat'
  if (isAuthenticated && (isRoot || isAuthRoute)) {
    const url = request.nextUrl.clone();
    url.pathname = "/chat";
    url.search = "";
    return NextResponse.redirect(url);
  }

  // 2. Protected routes ('/chat', '/dashboard') -> require authenticated session cookie
  if (!isAuthenticated && isProtectedRoute) {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}
