import { NextResponse } from "next/server";
import { serverClient } from "@/lib/supabase";
import { createStripeCheckoutSession } from "@/lib/payments";

export async function POST(req: Request) {
  const supabase = serverClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const origin =
    process.env.NEXT_PUBLIC_SITE_URL ||
    new URL(req.url).origin;

  try {
    const url = await createStripeCheckoutSession(
      user.id,
      user.email ?? null,
      origin.replace(/\/$/, "")
    );
    return NextResponse.json({ url });
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : "checkout failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
