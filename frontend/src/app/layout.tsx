import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Enterprise AI Assistant",
  description: "Next.js frontend with Supabase authentication",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-slate-50 text-slate-900">
        <main className="flex min-h-screen flex-col">{children}</main>
      </body>
    </html>
  );
}
