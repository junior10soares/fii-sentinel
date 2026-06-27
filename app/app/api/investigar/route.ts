import { NextResponse } from "next/server";

import { checkRateLimit, getClientIp, hashIp } from "@/lib/rate-limit";
import { getSupabaseAdmin } from "@/lib/supabase/admin";
import { tickerValido } from "@/lib/ticker";

const GITHUB_REPO = "junior10soares/fii-sentinel";
const WORKFLOW_FILE = "cron-investigar.yml";
const JANELA_RECENTE_MS = 30 * 60_000;

export async function POST(request: Request) {
  const ipHash = hashIp(getClientIp(request));

  const permitido = await checkRateLimit(ipHash);
  if (!permitido) {
    return NextResponse.json(
      { error: "Muitas requisições. Tente novamente em um minuto." },
      { status: 429 }
    );
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Corpo da requisição precisa ser JSON." }, { status: 400 });
  }

  const tickerBruto = (body as { ticker?: unknown } | null)?.ticker;
  const ticker = typeof tickerBruto === "string" ? tickerBruto.trim().toUpperCase() : "";

  if (!tickerValido(ticker)) {
    return NextResponse.json(
      { error: "Ticker inválido. Use o formato de 4 letras + 11, ex: KNRI11." },
      { status: 400 }
    );
  }

  const supabase = getSupabaseAdmin();
  const { data: ultimaAnalise } = await supabase
    .from("analises")
    .select("status, created_at")
    .eq("ticker", ticker)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  // só bloqueia reprocessamento se a última tentativa terminou bem — uma
  // falha recente (status != concluida) nunca deve travar o usuário 30min
  // sem conseguir tentar de novo.
  if (
    ultimaAnalise?.status === "concluida" &&
    Date.now() - new Date(ultimaAnalise.created_at).getTime() < JANELA_RECENTE_MS
  ) {
    return NextResponse.json({
      message: `${ticker} já foi investigado recentemente. Veja o resultado na página do ticker.`,
    });
  }

  const ghPat = process.env.GH_PAT;
  if (!ghPat) {
    console.error("GH_PAT não configurado — não é possível disparar workflow_dispatch.");
    return NextResponse.json(
      { error: "Disparo de investigação não está disponível neste ambiente." },
      { status: 503 }
    );
  }

  const resposta = await fetch(
    `https://api.github.com/repos/${GITHUB_REPO}/actions/workflows/${WORKFLOW_FILE}/dispatches`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${ghPat}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ ref: "main", inputs: { ticker } }),
    }
  );

  if (!resposta.ok) {
    console.error("Erro ao disparar workflow_dispatch:", resposta.status, await resposta.text());
    return NextResponse.json(
      { error: "Não foi possível iniciar a investigação. Tente novamente." },
      { status: 502 }
    );
  }

  return NextResponse.json(
    { message: `Investigando ${ticker}. Volte em ~1 minuto.` },
    { status: 202 }
  );
}
