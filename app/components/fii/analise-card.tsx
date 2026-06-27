import Link from "next/link";
import { ViewTransition } from "react";
import { ArrowUpRight } from "lucide-react";

import { Card } from "@/components/ui/card";
import { ScoreNumber } from "@/components/fii/score-number";
import { SeverityBadge, NenhumaContradicaoBadge } from "@/components/fii/severity-badge";
import { FAIXA_COLOR_CLASS, faixaDoScore } from "@/lib/score";
import { cn } from "@/lib/utils";
import type { AnaliseRow, Severidade } from "@/lib/types";

function piorSeveridade(severidades: Severidade[]): Severidade | null {
  if (severidades.includes("alta")) return "alta";
  if (severidades.includes("media")) return "media";
  if (severidades.includes("baixa")) return "baixa";
  return null;
}

export function AnaliseCard({ analise }: { analise: AnaliseRow }) {
  const score = analise.score ?? analise.resultado?.score_final ?? null;
  const contradicoes = analise.resultado?.contradicoes ?? [];
  const pior = piorSeveridade(contradicoes.map((c) => c.severidade));

  return (
    <Link href={`/${analise.ticker}`} className={cn("group", pior === "alta" && "sm:col-span-2")}>
      <ViewTransition name={`analise-${analise.ticker}`}>
        <Card className="h-full justify-between gap-4 p-5 transition-colors hover:border-accent/50">
          <div className="flex items-start justify-between gap-3">
            <h3 className="font-serif text-xl font-medium">{analise.ticker}</h3>
            <ArrowUpRight
              className="size-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100"
              aria-hidden="true"
            />
          </div>

          {score !== null && (
            <div className="flex items-baseline gap-1.5">
              <ScoreNumber
                value={score}
                className={cn("font-serif text-3xl font-semibold", FAIXA_COLOR_CLASS[faixaDoScore(score)])}
              />
              <span className="text-sm text-muted-foreground">/100</span>
            </div>
          )}

          <div>{pior ? <SeverityBadge severidade={pior} /> : <NenhumaContradicaoBadge />}</div>
        </Card>
      </ViewTransition>
    </Link>
  );
}
