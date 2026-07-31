-- Local E2E test schema (mirrors website/supabase profiles + usage_ledger).
-- No auth.users FK — test user UUID is provisioned directly.

create extension if not exists "pgcrypto";

create table if not exists profiles (
  id uuid primary key,
  tier text not null default 'free',
  litellm_key text,
  persona text default '',
  preferences text default '',
  session_count int not null default 0,
  trial_used boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists usage_ledger (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  session_id text not null,
  event_type text not null check (event_type in ('session_start', 'inference')),
  model_used text,
  tokens_in int default 0,
  tokens_out int default 0,
  cost_usd numeric(10,8) default 0,
  tier text not null check (tier in ('trial', 'free', 'pro')),
  created_at timestamptz not null default now()
);

create or replace function check_trial_session_limit()
returns trigger language plpgsql as $$
declare
  _tier text;
  _trial_used boolean;
  _session_count int;
begin
  select tier, trial_used, session_count
    into _tier, _trial_used, _session_count
    from profiles where id = new.user_id;
  if _tier = 'free' and _trial_used = false then
    new.tier := 'trial';
    update profiles set trial_used = true, session_count = session_count + 1
      where id = new.user_id;
  end if;
  if new.event_type = 'session_start' and _tier = 'trial' and _session_count >= 1 then
    raise exception 'trial_session_limit_reached';
  end if;
  return new;
end;
$$;

drop trigger if exists trg_check_trial_session on usage_ledger;
create trigger trg_check_trial_session
  before insert on usage_ledger
  for each row
  when (new.event_type = 'session_start')
  execute function check_trial_session_limit();

create index if not exists usage_ledger_user_event_idx
  on usage_ledger(user_id, event_type, created_at desc);
