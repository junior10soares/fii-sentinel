export type FaixaScore = "solido" | "atencao" | "alerta";

const LIMITE_SOLIDO = 75;
const LIMITE_ATENCAO = 50;

export function faixaDoScore(score: number): FaixaScore {
  if (score >= LIMITE_SOLIDO) return "solido";
  if (score >= LIMITE_ATENCAO) return "atencao";
  return "alerta";
}

export const FAIXA_LABEL: Record<FaixaScore, string> = {
  solido: "Sólido",
  atencao: "Atenção",
  alerta: "Alerta",
};

export const FAIXA_COLOR_CLASS: Record<FaixaScore, string> = {
  solido: "text-severity-ok",
  atencao: "text-severity-media",
  alerta: "text-severity-alta",
};
