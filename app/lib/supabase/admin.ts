import { createClient } from "@supabase/supabase-js";

/**
 * Client com service role — ignora RLS. Só pode ser usado em código
 * server-only (Route Handlers), nunca importado por um Client Component.
 */
export function getSupabaseAdmin() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

  if (!url || !key) {
    throw new Error(
      "SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY precisam estar definidos"
    );
  }

  return createClient(url, key, { auth: { persistSession: false } });
}
