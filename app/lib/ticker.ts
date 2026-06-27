// Mesma regra validada em pipeline/agents/coletor/fundamentus.py e em
// .github/workflows/cron-investigar.yml — duplicada entre Python/YAML/TS
// porque o projeto não tem (e não deveria ter) um pacote cross-linguagem
// (CLAUDE.md). Dentro do TS, porém, search-bar.tsx e a rota usam esta mesma
// constante — nada de duplicar de novo aqui dentro.
export const FORMATO_TICKER = /^[A-Z]{4}11$/;

export function tickerValido(valor: string): boolean {
  return FORMATO_TICKER.test(valor.toUpperCase());
}
