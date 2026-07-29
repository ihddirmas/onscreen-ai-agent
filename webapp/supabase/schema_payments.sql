-- Payments schema: additive columns on profiles + idempotent event log.
-- Run AFTER website/supabase/schema.sql (the profiles table must already exist).

alter table profiles
  add column if not exists stripe_customer_id text,
  add column if not exists stripe_subscription_id text,
  add column if not exists subscription_status text not null default 'inactive',
  add column if not exists billing_provider text not null default '';

-- Idempotency log: prevents double-processing when Stripe/Razorpay retry
-- a webhook delivery. Both providers guarantee a unique event_id per event.
create table if not exists payment_events (
  id bigint primary key generated always as identity,
  provider text not null,            -- 'stripe' | 'razorpay'
  event_id text not null,            -- unique per event per provider
  type text not null,                -- e.g. 'checkout.session.completed'
  payload jsonb,
  processed_at timestamptz not null default now(),
  unique (provider, event_id)
);
