import { createClient } from "@supabase/supabase-js";

/**
 * Client anônimo (publishable key) — usado pelos Server Components de
 * leitura pública. Sujeito a RLS (supabase/migrations/0003_rls.sql):
 * só `fiis` e `analises` são legíveis por essa chave.
 */
export function getSupabaseAnon() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_URL e NEXT_PUBLIC_SUPABASE_ANON_KEY precisam estar definidos"
    );
  }

  return createClient(url, key, { auth: { persistSession: false } });
}
