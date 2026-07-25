-- Parakeet web app schema. Run in the Supabase SQL editor.

-- pgvector for embeddings
create extension if not exists vector;

-- One profile row per auth user.
create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  tier text not null default 'free',            -- free | pro
  litellm_key text,                              -- the user's Parakeet key (sk-...)
  persona text default '',                       -- auto-derived summary from their docs
  preferences text default '',                   -- user-editable ("answer coding in Python")
  created_at timestamptz not null default now()
);

-- Uploaded documents.
create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  filename text not null,
  storage_path text not null,
  status text not null default 'processing',     -- processing | ready | error
  created_at timestamptz not null default now()
);

-- Chunked + embedded content (RAG index). 384 = bge-small-en-v1.5 dims.
create table if not exists doc_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references documents(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  content text not null,
  embedding vector(384)
);

create index if not exists doc_chunks_embedding_idx
  on doc_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);
create index if not exists doc_chunks_user_idx on doc_chunks(user_id);

-- Similarity search for one user, callable from the server (service role).
create or replace function match_doc_chunks(
  p_user_id uuid,
  query_embedding vector(384),
  match_count int default 5
)
returns table (content text, similarity float)
language sql stable
as $$
  select c.content, 1 - (c.embedding <=> query_embedding) as similarity
  from doc_chunks c
  where c.user_id = p_user_id
  order by c.embedding <=> query_embedding
  limit match_count;
$$;

-- Row Level Security: users see only their own rows. The server uses the
-- service-role key (which bypasses RLS) for the desktop search endpoint.
alter table profiles enable row level security;
alter table documents enable row level security;
alter table doc_chunks enable row level security;

create policy "own profile"  on profiles  for all using (auth.uid() = id)       with check (auth.uid() = id);
create policy "own docs"     on documents for all using (auth.uid() = user_id)  with check (auth.uid() = user_id);
create policy "own chunks"   on doc_chunks for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Auto-create a profile row when a new auth user signs up.
create or replace function handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.profiles (id) values (new.id) on conflict do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();

-- Storage bucket for the raw uploaded files (private).
insert into storage.buckets (id, name, public)
values ('documents', 'documents', false)
on conflict (id) do nothing;

create policy "own files read"   on storage.objects for select using (bucket_id = 'documents' and auth.uid()::text = (storage.foldername(name))[1]);
create policy "own files write"  on storage.objects for insert with check (bucket_id = 'documents' and auth.uid()::text = (storage.foldername(name))[1]);
