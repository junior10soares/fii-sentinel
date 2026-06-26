create or replace function buscar_documentos_similares(
  p_ticker text,
  query_embedding vector(768),
  match_count int default 5
)
returns table (
  id uuid,
  fonte text,
  conteudo text,
  metadata jsonb,
  similaridade float
)
language sql stable
as $$
  select id, fonte, conteudo, metadata, 1 - (embedding <=> query_embedding) as similaridade
  from documentos
  where ticker = p_ticker
  order by embedding <=> query_embedding
  limit match_count;
$$;
