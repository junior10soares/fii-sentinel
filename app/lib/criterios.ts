// Nomes vêm de pipeline/agents/scorer/score.py (snake_case, não pensados pra exibição).
export const CRITERIO_LABEL: Record<string, string> = {
  dividendos: "Dividendos",
  ativos: "Ativos",
  transparencia: "Transparência",
  saude_financeira: "Saúde financeira",
  tendencia: "Tendência",
};

export function labelDoCriterio(nome: string): string {
  return CRITERIO_LABEL[nome] ?? nome;
}
