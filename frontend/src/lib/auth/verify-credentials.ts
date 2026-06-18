import { createClient } from "@/lib/supabase/server";

import type { AppSession } from "./session";

export async function verifyCredentials(
  username: string,
  password: string,
): Promise<AppSession | null> {
  const trimmedUsername = username.trim();

  if (!trimmedUsername || !password) {
    return null;
  }

  const supabase = await createClient();
  const { data, error } = await supabase
    .from("users")
    .select("id, username, password")
    .eq("username", trimmedUsername)
    .maybeSingle();

  if (error || !data) {
    return null;
  }

  if (data.password !== password) {
    return null;
  }

  return {
    id: data.id,
    username: data.username,
  };
}
