import "server-only";

import Stripe from "stripe";
import { adminClient } from "@/lib/supabase";
import { mintKey, updateKeyBudget } from "@/lib/litellm";

const PRO_TIER = "pro";
const FREE_TIER = "free";

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`${name} is not set`);
  return value;
}

function stripeClient(): Stripe {
  return new Stripe(requireEnv("STRIPE_SECRET_KEY"));
}

export async function createStripeCheckoutSession(
  userId: string,
  email: string | null,
  origin: string
): Promise<string> {
  const stripe = stripeClient();
  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    line_items: [{ price: requireEnv("STRIPE_PRICE_ID_PRO"), quantity: 1 }],
    success_url: `${origin}/dashboard?checkout=success`,
    cancel_url: `${origin}/pricing?checkout=cancelled`,
    customer_email: email ?? undefined,
    client_reference_id: userId,
    subscription_data: { metadata: { user_id: userId } },
    metadata: { user_id: userId },
  });
  if (!session.url) throw new Error("Stripe did not return a checkout URL");
  return session.url;
}

async function recordEventOnce(
  provider: string,
  eventId: string,
  eventType: string,
  payload: unknown
): Promise<boolean> {
  const admin = adminClient();
  const { error } = await admin.from("payment_events").insert({
    provider,
    event_id: eventId,
    type: eventType,
    payload,
  });
  if (!error) return true;
  if (error.code === "23505") return false; // unique violation — replay
  throw error;
}

async function activateSubscription(userId: string, provider: string) {
  const admin = adminClient();
  const { data: profile } = await admin
    .from("profiles")
    .select("litellm_key")
    .eq("id", userId)
    .maybeSingle();

  let key = profile?.litellm_key as string | null;
  if (key) {
    await updateKeyBudget(key, PRO_TIER);
  } else {
    key = await mintKey(userId, PRO_TIER);
  }

  await admin
    .from("profiles")
    .update({
      tier: PRO_TIER,
      subscription_status: "active",
      billing_provider: provider,
      litellm_key: key,
    })
    .eq("id", userId);
}

async function cancelSubscription(userId: string, provider: string) {
  const admin = adminClient();
  const { data: profile } = await admin
    .from("profiles")
    .select("litellm_key")
    .eq("id", userId)
    .maybeSingle();

  const key = profile?.litellm_key as string | null;
  if (key) await updateKeyBudget(key, FREE_TIER);

  await admin
    .from("profiles")
    .update({
      tier: FREE_TIER,
      subscription_status: "canceled",
      billing_provider: provider,
    })
    .eq("id", userId);
}

const ACTIVE = new Set(["active", "trialing"]);
const INACTIVE = new Set(["canceled", "unpaid", "incomplete_expired"]);

export async function handleStripeEvent(event: Stripe.Event) {
  const isNew = await recordEventOnce("stripe", event.id, event.type, event);
  if (!isNew) return;

  const admin = adminClient();
  const obj = event.data.object as Stripe.Checkout.Session | Stripe.Subscription;

  if (event.type === "checkout.session.completed") {
    const session = obj as Stripe.Checkout.Session;
    const userId =
      session.client_reference_id || session.metadata?.user_id || null;
    if (!userId) return;
    await admin
      .from("profiles")
      .update({
        billing_provider: "stripe",
        stripe_customer_id: session.customer as string | null,
        stripe_subscription_id: session.subscription as string | null,
      })
      .eq("id", userId);
    await activateSubscription(userId, "stripe");
    return;
  }

  if (event.type === "customer.subscription.updated") {
    const sub = obj as Stripe.Subscription;
    const userId = sub.metadata?.user_id;
    if (!userId) return;
    if (ACTIVE.has(sub.status)) await activateSubscription(userId, "stripe");
    else if (INACTIVE.has(sub.status)) await cancelSubscription(userId, "stripe");
    else {
      await admin
        .from("profiles")
        .update({ subscription_status: sub.status })
        .eq("id", userId);
    }
    return;
  }

  if (event.type === "customer.subscription.deleted") {
    const sub = obj as Stripe.Subscription;
    const userId = sub.metadata?.user_id;
    if (!userId) return;
    await cancelSubscription(userId, "stripe");
  }
}

export function verifyStripeWebhook(
  payload: string | Buffer,
  signature: string
): Stripe.Event {
  return stripeClient().webhooks.constructEvent(
    payload,
    signature,
    requireEnv("STRIPE_WEBHOOK_SECRET")
  );
}
