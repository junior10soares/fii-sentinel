import { labelDoCriterio } from "@/lib/criterios";
import type { CriterioScore } from "@/lib/types";

export function CriterioBar({ criterio }: { criterio: CriterioScore }) {
  const pontos = Math.round(criterio.pontos);

  return (
    <div className="space-y-1.5">
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-sm font-medium">{labelDoCriterio(criterio.nome)}</span>
        <span className="text-sm text-muted-foreground" style={{ fontVariantNumeric: "tabular-nums" }}>
          {pontos}/100 <span className="text-xs">· peso {Math.round(criterio.peso * 100)}%</span>
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted" role="presentation">
        {/* scaleX em vez de width: anima via transform (GPU), nunca reflow */}
        <div
          className="h-full w-full origin-left rounded-full bg-primary transition-transform duration-500 ease-out"
          style={{ transform: `scaleX(${Math.min(100, Math.max(0, pontos)) / 100})` }}
        />
      </div>
      <p className="text-xs text-muted-foreground">{criterio.justificativa}</p>
    </div>
  );
}
