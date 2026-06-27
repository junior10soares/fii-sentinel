// Espelha os schemas Pydantic de pipeline/agents/{analista,scorer}/schemas.py.
// resultado é jsonb sem schema no Postgres — esses tipos são só do lado do
// app/, não há contrato compartilhado de verdade entre Python e TS.

export type Severidade = "baixa" | "media" | "alta";

export interface Contradicao {
  trecho_relatorio: string;
  dado_contraditorio: string;
  explicacao: string;
  severidade: Severidade;
}

export interface CriterioScore {
  nome: string;
  peso: number;
  pontos: number;
  justificativa: string;
}

export interface MarcoTimeline {
  periodo: string;
  narrativa: string;
}

// graph/nodes.py:construir_no_sucesso preenche os 3 arrays sempre (podem vir
// vazios, nunca ausentes) quando resultado existe — refletido aqui como
// obrigatório. Ainda assim, todo consumidor valida com Array.isArray antes
// de iterar: resultado é jsonb sem schema, uma linha fora desse contrato
// (ex: colada à mão) não pode quebrar a página.
export interface ResultadoAnalise {
  ticker: string;
  score_final: number;
  criterios: CriterioScore[];
  timeline: MarcoTimeline[];
  contradicoes: Contradicao[];
}

export interface AnaliseRow {
  id: string;
  ticker: string;
  status: string;
  score: number | null;
  resultado: ResultadoAnalise | null;
  created_at: string;
}
