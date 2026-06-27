import { AnaliseCard } from "@/components/fii/analise-card";
import { SearchBar } from "@/components/fii/search-bar";
import { getSupabaseAnon } from "@/lib/supabase/client";
import type { AnaliseRow } from "@/lib/types";

// sem sinal de dinamismo (sem cookies/headers/params), o Next prerenderiza
// esta página como estática no build — "análises recentes" ficaria congelada
// na data do deploy. Novas investigações chegam via cron/GitHub Actions, não
// via redeploy, então essa página precisa renderizar de novo a cada request.
export const dynamic = "force-dynamic";

async function buscarAnalisesRecentes(): Promise<AnaliseRow[]> {
  const supabase = getSupabaseAnon();
  const { data, error } = await supabase
    .from("analises")
    .select("id, ticker, status, score, resultado, created_at")
    .eq("status", "concluida")
    .order("created_at", { ascending: false })
    .limit(30);

  if (error) {
    console.error("Erro ao buscar análises recentes:", error.message);
    return [];
  }

  // mais de uma investigação por ticker é normal (reprocessamento) — a home
  // mostra só a mais recente de cada, o histórico completo fica pra depois.
  const vistos = new Set<string>();
  const unicas: AnaliseRow[] = [];
  for (const analise of data ?? []) {
    if (vistos.has(analise.ticker)) continue;
    vistos.add(analise.ticker);
    unicas.push(analise);
  }
  return unicas.slice(0, 12);
}

export default async function Home() {
  const analises = await buscarAnalisesRecentes();

  return (
    <div className="flex flex-1 flex-col">
      <header className="border-b border-border px-6 py-5 sm:px-10">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="font-serif text-2xl font-medium">FII Sentinel</h1>
          <SearchBar />
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-10 sm:px-10">
        <p className="mb-8 max-w-2xl text-muted-foreground">
          Cruzamos o discurso do relatório gerencial de um FII com os números reais e
          apontamos contradições — não só exibimos métricas.
        </p>

        {analises.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border p-10 text-center text-muted-foreground">
            Nenhuma análise ainda. Busque um ticker para começar.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {analises.map((analise) => (
              <AnaliseCard key={analise.id} analise={analise} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
