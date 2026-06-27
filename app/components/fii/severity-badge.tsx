import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Severidade } from "@/lib/types";

const CONFIG: Record<Severidade, { label: string; icon: typeof Info; classes: string }> = {
  alta: {
    label: "Alta",
    icon: AlertTriangle,
    // sólido + texto branco (não o /10 suave dos outros) — severidade alta
    // precisa parecer alarmante de verdade, não um badge cinza.
    classes: "border-transparent bg-severity-alta text-white [a]:hover:bg-severity-alta/90",
  },
  media: {
    label: "Média",
    icon: AlertCircle,
    classes: "border-severity-media/20 bg-severity-media/10 text-severity-media",
  },
  baixa: {
    label: "Baixa",
    icon: Info,
    classes: "border-severity-baixa/20 bg-severity-baixa/10 text-severity-baixa",
  },
};

export function SeverityBadge({ severidade }: { severidade: Severidade }) {
  const { label, icon: Icon, classes } = CONFIG[severidade];

  return (
    <Badge
      className={cn(classes, severidade === "alta" && "animate-severidade-alta")}
    >
      <Icon data-icon="inline-start" aria-hidden="true" />
      Contradição {label}
    </Badge>
  );
}

export function NenhumaContradicaoBadge() {
  return (
    <Badge className="border-severity-ok/20 bg-severity-ok/10 text-severity-ok">
      <CheckCircle2 data-icon="inline-start" aria-hidden="true" />
      Sem contradições
    </Badge>
  );
}
