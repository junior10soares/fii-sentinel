import { ArrowLeft } from "lucide-react";
import type { Metadata } from "next";
import Link from "next/link";
import { ViewTransition } from "react";

import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ContradicaoCard } from "@/components/fii/contradicao-card";
import { CriterioBar } from "@/components/fii/criterio-bar";
import { InvestigarButton } from "@/components/fii/investigar-button";
import { ScoreNumber } from "@/components/fii/score-number";
import { NenhumaContradicaoBadge } from "@/components/fii/severity-badge";
import { TimelineList } from "@/components/fii/timeline-list";
import { FAIXA_COLOR_CLASS, FAIXA_LABEL, faixaDoScore } from "@/lib/score";
import { getSupabaseAnon } from "@/lib/supabase/client";
import type { AnaliseRow } from "@/lib/types";

async function buscarAnalise(ticker: string): Promise<AnaliseRow | null> {
  const supabase = getSupabaseAnon();
  const { data, error } = await supabase
    .from("analises")
    .select("id, ticker, status, score, resultado, created_at")
    .eq("ticker", ticker)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  if (error) {
    console.error(`Erro ao buscar análise de ${ticker}:`, error.message);
    return null;
  }
  return data;
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ ticker: string }>;
}): Promise<Metadata> {
  const { ticker } = await params;
  return { title: `${ticker.toUpperCase()} — FII Sentinel` };
}

export default async function TickerPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const { ticker: tickerParam } = await params;
  const ticker = tickerParam.toUpperCase();
  const analise = await buscarAnalise(ticker);
  const resultado = analise?.status === "concluida" ? analise.resultado : null;
  const score = resultado?.score_final ?? analise?.score ?? null;
  // resultado é jsonb sem schema no Postgres — nunca confiar que o formato
  // bate com o tipo TS (ex: uma linha colada à mão na Fase 1) sem checar.
  const criterios = Array.isArray(resultado?.criterios) ? resultado.criterios : [];
  const contradicoes = Array.isArray(resultado?.contradicoes) ? resultado.contradicoes : [];
  const timeline = Array.isArray(resultado?.timeline) ? resultado.timeline : [];
  const resultadoValido = criterios.length > 0;

  return (
    <div className="flex flex-1 flex-col">
      <header className="border-b border-border px-6 py-5 sm:px-10">
        <div className="mx-auto max-w-4xl">
          <Link
            href="/"
            transitionTypes={["nav-back"]}
            className="inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ArrowLeft className="size-4" aria-hidden="true" />
            FII Sentinel
          </Link>
        </div>
      </header>

      <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-10 sm:px-10">
        <ViewTransition name={`analise-${ticker}`}>
          <div className="flex flex-wrap items-baseline justify-between gap-4">
            <h1 className="font-serif text-3xl font-medium">{ticker}</h1>
            {score !== null && (
              <div className="flex items-baseline gap-2">
                <ScoreNumber
                  value={score}
                  className={`font-serif text-5xl font-semibold ${FAIXA_COLOR_CLASS[faixaDoScore(score)]}`}
                />
                <span className="text-muted-foreground">
                  /100 · {FAIXA_LABEL[faixaDoScore(score)]}
                </span>
              </div>
            )}
          </div>
        </ViewTransition>

        {!analise && (
          <Card className="mt-8 items-center gap-4 p-10 text-center">
            <p className="text-muted-foreground">{ticker} ainda não foi investigado.</p>
            <InvestigarButton ticker={ticker} />
          </Card>
        )}

        {analise && analise.status !== "concluida" && (
          <Card className="mt-8 items-center gap-2 p-10 text-center">
            <p className="text-muted-foreground">
              A última investigação de {ticker} não foi concluída (status: {analise.status}).
            </p>
          </Card>
        )}

        {analise?.status === "concluida" && !resultadoValido && (
          <Card className="mt-8 items-center gap-2 p-10 text-center">
            <p className="text-muted-foreground">
              A investigação de {ticker} terminou, mas sem dados de score pra exibir.
            </p>
          </Card>
        )}

        {resultadoValido && (
          <div className="mt-10 space-y-12">
            <section aria-labelledby="criterios-heading">
              <h2 id="criterios-heading" className="mb-4 font-serif text-lg font-medium">
                Critérios do score
              </h2>
              <Card className="gap-6 p-6">
                {criterios.map((criterio) => (
                  <CriterioBar key={criterio.nome} criterio={criterio} />
                ))}
              </Card>
            </section>

            <section aria-labelledby="contradicoes-heading">
              <div className="mb-4 flex items-center justify-between">
                <h2 id="contradicoes-heading" className="font-serif text-lg font-medium">
                  Contradições encontradas
                </h2>
                {contradicoes.length === 0 && <NenhumaContradicaoBadge />}
              </div>
              {contradicoes.length > 0 && (
                <div className="space-y-4">
                  {contradicoes.map((contradicao, index) => (
                    <ContradicaoCard key={index} contradicao={contradicao} />
                  ))}
                </div>
              )}
            </section>

            {timeline.length > 0 && (
              <section aria-labelledby="timeline-heading">
                <h2 id="timeline-heading" className="mb-6 font-serif text-lg font-medium">
                  Linha do tempo
                </h2>
                <Separator className="mb-6" />
                <TimelineList marcos={timeline} />
              </section>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
