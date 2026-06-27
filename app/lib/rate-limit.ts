import { createHash } from "node:crypto";

import { getSupabaseAdmin } from "@/lib/supabase/admin";

// Mecanismo (janela fixa em Postgres puro) reaproveitado de
// portfolio-ia/lib/db/supabase/rate-limit.ts — mesmo problema, mesma solução
// já validada em produção lá. O limite em si é menor aqui de propósito
// (5, não 10): essa rota dispara um workflow_dispatch real no GitHub Actions
// por chamada, uma ação bem mais cara que o que portfolio-ia limitava.
const WINDOW_MS = 60_000;
const MAX_REQUESTS_PER_WINDOW = 5;

export function hashIp(ip: string): string {
  return createHash("sha256").update(ip).digest("hex");
}

export function getClientIp(req: Request): string {
  // NextRequest.ip/.geo foram removidos no Next 15 — sem helper de plataforma,
  // a defesa é ler x-forwarded-for pelo ÚLTIMO hop, não o primeiro. Cada proxy
  // na cadeia ANEXA o endereço de quem se conectou a ele; um cliente malicioso
  // só controla o que vem ANTES do hop confiável (a borda da plataforma), nunca
  // o último valor anexado. Ler o primeiro (o que era feito antes) deixa
  // qualquer cliente forjar um IP novo por requisição e burlar o rate limit.
  const forwarded = req.headers.get("x-forwarded-for");
  const ultimoHop = forwarded?.split(",").pop()?.trim();
  return ultimoHop || "unknown";
}

export async function checkRateLimit(ipHash: string): Promise<boolean> {
  // ponytail: check-then-act sem lock/transação — duas requisições concorrentes
  // do mesmo IP podem ambas ler a contagem antes de qualquer uma escrever,
  // permitindo passar um pouco do limite. Mesmo tradeoff já aceito no padrão
  // original do portfolio-ia; upgrade pra incremento atômico (RPC com UPSERT
  // ON CONFLICT) se isso comprovadamente virar abuso real.
  const supabase = getSupabaseAdmin();
  const now = new Date();

  const { data: existing } = await supabase
    .from("rate_limit_counters")
    .select("window_start, count")
    .eq("ip_hash", ipHash)
    .maybeSingle();

  const windowExpired =
    !existing || now.getTime() - new Date(existing.window_start).getTime() > WINDOW_MS;

  if (windowExpired) {
    await supabase
      .from("rate_limit_counters")
      .upsert({ ip_hash: ipHash, window_start: now.toISOString(), count: 1 });
    return true;
  }

  if (existing.count >= MAX_REQUESTS_PER_WINDOW) {
    return false;
  }

  await supabase
    .from("rate_limit_counters")
    .update({ count: existing.count + 1 })
    .eq("ip_hash", ipHash);

  return true;
}
