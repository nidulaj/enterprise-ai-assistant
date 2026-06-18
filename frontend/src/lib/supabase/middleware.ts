import { NextResponse, type NextRequest } from "next/server";

import { getSessionFromRequest } from "@/lib/auth/session";

export async function updateSession(request: NextRequest) {
  const session = getSessionFromRequest(request);
  const pathname = request.nextUrl.pathname;
  const isAuthRoute = pathname.startsWith("/login");

  if (!session && pathname.startsWith("/dashboard")) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  if (session && isAuthRoute) {
    const url = request.nextUrl.clone();
    url.pathname = "/dashboard";
    url.search = "";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}
