-- Payments schema: additive columns on profiles + idempotent event log.
-- Run AFTER website/supabase/schema.sql (the profiles table must already exist).

alter table profiles
  add column if not exists stripe_customer_id text,
  add column if not exists stripe_subscription_id text,
  add column if not exists subscription_status text not null default 'inactive',
  add column if not exists billing_provider text not null default '';

-- Trial usage tracking (session cap for free/hosted-first onboarding)
alter table profiles
  add column if not exists trial_used boolean not null default false,
  add column if not exists session_count integer not null default 0;

-- Usage ledger: one row per session event (used for trial cap + audit).
create table if not exists usage_ledger (
  id bigint primary key generated always as identity,
  user_id uuid not null references auth.users(id) on delete cascade,
  session_id text not null,
  event_type text not null,            -- 'session_start' | 'session_end'
  tier text not null,                   -- 'trial' | 'free' | 'pro'
  created_at timestamptz not null default now()
);
create index if not exists usage_ledger_user_idx on usage_ledger(user_id, created_at desc);

-- RPC for the desktop app to check session eligibility.
create or replace function check_session(p_user_id uuid)
returns jsonb
language plpgsql stable
as $$
declare
  _tier text;
  _trial_used boolean;
  _session_count integer;
begin
  select tier, trial_used, session_count
    into _tier, _trial_used, _session_count
    from profiles
    where id = p_user_id;

  if not found then
    return jsonb_build_object('can_start', true, 'tier', 'unknown', 'session_count', 0, 'trial_remaining', 0);
  end if;

  if _tier = 'pro' then
    return jsonb_build_object('can_start', true, 'tier', 'pro', 'session_count', _session_count, 'trial_remaining', -1);
  end if;

  return jsonb_build_object(
    'can_start', _session_count < 1,
    'tier', _tier,
    'session_count', _session_count,
    'trial_remaining', greatest(0, 1 - _session_count)
  );
end;
$$;

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
