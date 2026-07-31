import { NextRequest, NextResponse } from "next/server";
import { handleStripeEvent, verifyStripeWebhook } from "@/lib/payments";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  const payload = await req.text();
  const signature = req.headers.get("stripe-signature");
  if (!signature) {
    return NextResponse.json({ error: "missing signature" }, { status: 400 });
  }

  let event;
  try {
    event = verifyStripeWebhook(payload, signature);
  } catch {
    return NextResponse.json({ error: "invalid signature" }, { status: 400 });
  }

  try {
    await handleStripeEvent(event);
  } catch (e: unknown) {
    const message = e instanceof Error ? e.message : "handler failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }

  return NextResponse.json({ received: true });
}
