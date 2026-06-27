-- Leitura pública (client anônimo do app/) restrita a fiis e analises.
-- documentos/cache_scraping/rate_limit_counters ficam com RLS habilitado e
-- SEM policy nenhuma — acesso só via service_role (que ignora RLS), nunca
-- pelo client anônimo. service_role sempre ignora RLS, então o pipeline
-- (Fases 2-7) e a rota app/api/investigar (service role) continuam intactos.

alter table fiis enable row level security;
alter table analises enable row level security;
alter table documentos enable row level security;
alter table cache_scraping enable row level security;
alter table rate_limit_counters enable row level security;

create policy "fiis: leitura publica"
  on fiis for select
  to anon
  using (true);

create policy "analises: leitura publica"
  on analises for select
  to anon
  using (true);
