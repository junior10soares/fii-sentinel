import { Card } from "@/components/ui/card";
import { SeverityBadge } from "@/components/fii/severity-badge";
import type { Contradicao } from "@/lib/types";

export function ContradicaoCard({ contradicao }: { contradicao: Contradicao }) {
  return (
    <Card className="gap-3 p-5">
      <SeverityBadge severidade={contradicao.severidade} />
      <blockquote className="border-l-2 border-border pl-3 font-serif text-base italic text-foreground/90">
        “{contradicao.trecho_relatorio}”
      </blockquote>
      <div className="space-y-1 text-sm">
        <p>
          <span className="font-medium text-foreground">O que os dados mostram: </span>
          <span className="text-muted-foreground">{contradicao.dado_contraditorio}</span>
        </p>
        <p className="text-muted-foreground">{contradicao.explicacao}</p>
      </div>
    </Card>
  );
}
