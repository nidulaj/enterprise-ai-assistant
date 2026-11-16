import { redirect } from "next/navigation";
import { getSession } from "@/lib/auth/session";

export default async function DashboardPage() {
  const session = await getSession();

  if (!session) {
    redirect("/login?next=/chat");
  }

  redirect("/chat");
}
