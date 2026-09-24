import { Suspense } from "react";

export const dynamic = "force-dynamic";

export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<div className="container" style={{ marginTop: 60 }}>Loading…</div>}>{children}</Suspense>;
}
