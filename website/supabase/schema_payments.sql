-- Payments addendum to schema.sql. Additive only — run after schema.sql.
-- Adds billing identity columns to profiles and a payment_events table for
-- webhook idempotency (Stripe and Razorpay both retry delivery on anything
-- other than a fast 2xx, so replaying an event must be a no-op).

alter table profiles add column if not exists stripe_customer_id text;
alter table profiles add column if not exists stripe_subscription_id text;
alter table profiles add column if not exists subscription_status text;
alter table profiles add column if not exists billing_provider text
  check (billing_provider in ('stripe', 'razorpay', 'none'));

-- Raw webhook events, keyed by (provider, event_id). The unique constraint
-- is what makes replay a no-op: a second insert for the same event raises a
-- unique-violation (23505), which the webhook handler treats as "already
-- processed, return 200" rather than reprocessing side effects.
create table if not exists payment_events (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  event_id text not null,
  type text not null,
  payload jsonb,
  processed_at timestamptz default now(),
  unique (provider, event_id)
);

alter table payment_events enable row level security;

-- Server-only table: no anon/user policies. The webhook handler uses the
-- service-role client (bypasses RLS), same as the rest of the payments flow.
