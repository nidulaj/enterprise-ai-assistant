import { redirect } from "next/navigation";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const queryString = new URLSearchParams(
    params as Record<string, string>,
  ).toString();
  redirect(queryString ? `/?${queryString}` : "/");
}
