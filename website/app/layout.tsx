import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Parakeet — your on-screen AI",
  description: "Login, pricing, credit usage, and reference documents for Parakeet.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
