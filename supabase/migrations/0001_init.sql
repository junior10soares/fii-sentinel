create extension if not exists vector;

create table fiis (
  ticker text primary key,
  nome text,
  created_at timestamptz not null default now()
);

create table analises (
  id uuid primary key default gen_random_uuid(),
  ticker text not null references fiis(ticker),
  status text not null default 'pendente',
  score numeric,
  resultado jsonb,
  created_at timestamptz not null default now()
);

create table documentos (
  id uuid primary key default gen_random_uuid(),
  ticker text not null,
  fonte text not null,
  conteudo text not null,
  embedding vector(768),
  metadata jsonb,
  created_at timestamptz not null default now()
);

create index documentos_embedding_hnsw
  on documentos using hnsw (embedding vector_cosine_ops);

create table cache_scraping (
  url text primary key,
  conteudo text not null,
  fetched_at timestamptz not null default now()
);

create table rate_limit_counters (
  ip_hash text primary key,
  window_start timestamptz not null,
  count int not null default 1
);
