# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é este projeto

Investigador autônomo de Fundos de Investimento Imobiliário (FIIs). O
diferencial não é exibir métricas — é cruzar o discurso do relatório
gerencial de um FII com os números reais e apontar contradições ("a gestora
disse que a vacância estava estabilizando, mas os dados mostram alta pelo 3º
mês consecutivo").

Plano completo (fases, arquitetura, critérios de saída por fase):
`/home/juniorsoares/.claude/plans/expressive-booping-marble.md`. Esse arquivo
é a fonte de verdade do roadmap — consulte-o ao iniciar cada fase.

## Princípio não-negociável: esqueleto andante primeiro

A Fase 1 prova o detector de contradições ponta a ponta com dado mínimo colado
à mão (sem scraper, sem RAG, sem LangGraph) antes de qualquer infraestrutura
real ser construída. Se o LLM não conseguir achar contradições de forma
coerente, isso precisa ser descoberto ali — não depois de semanas de scraping
e orquestração. Não adiante fases (ex: não monte o grafo LangGraph antes dos
agentes que ele orquestra já existirem testados isoladamente).

## Custo zero e disponibilidade 24h sem servidor próprio

Toda a stack roda em serviços com free tier que não dependem de uma máquina
ligada o tempo todo:

- **Compute pesado** (scraping com Playwright, parsing de PDF, embeddings,
  chamadas LLM, grafo LangGraph) roda via **GitHub Actions** (cron diário +
  `workflow_dispatch` sob demanda) — não em um servidor sempre ligado.
- **Banco vetorial + relacional**: **Supabase Postgres + pgvector**, não
  ChromaDB local — Render/Railway free tier dorme por inatividade e tem disco
  efêmero, perderia o índice a cada redeploy.
- **LLM**: **Gemini** (Google AI Studio free tier) como principal, **Groq**
  como alternativa rápida. Não usar a suposição de "Claude API free tier" do
  pitch original — a Anthropic não tem um free tier permanente generoso como o
  Gemini AI Studio.
- **Frontend**: só lê do Supabase e, para ticker não processado, dispara
  `workflow_dispatch` via API do GitHub — nunca executa lógica pesada.

Esse é o mesmo raciocínio já validado em produção no projeto irmão
`../portfolio-ia` (ver `portfolio-ia/CLAUDE.md`), que trocou Anthropic por
Gemini e roda 100% em serviços com free tier pelo mesmo motivo. O padrão de
rate limit em Postgres puro usado em `app/api/investigar` também é
reaproveitado literalmente de `portfolio-ia/lib/db/supabase/rate-limit.ts`.

## Decisões já tomadas (não reabrir sem motivo novo)

| Componente | Decisão | Por quê |
|---|---|---|
| Frontend | Next.js + Tailwind + shadcn/ui, deploy na Vercel | Streamlit não é coberto pelo plugin de design `ui-ux-pro-max` |
| Vector DB | Supabase Postgres + pgvector | Persistência real em free tier serverless |
| LLM | Gemini (principal), Groq (alternativa) | Free tier permanente e generoso |
| Backend HTTP | Nenhum (sem FastAPI sempre ligado) | Nada precisa servir HTTP síncrono do lado Python |
| Orquestração pesada | GitHub Actions (cron + `workflow_dispatch`) | Compute sob demanda, grátis, sem servidor ocioso |
| Repositório | Próprio e independente (`junior10soares/fii-sentinel`) | Portfólio — herda community health files de `junior10soares/.github` |

## O que não implementar nesta fase

Monitorar todos os FIIs do mercado (lista fixa pequena por enquanto, ex: top
10), dashboard comparativo entre fundos, alertas/notificações, autenticação de
usuário, chunking semântico sofisticado no RAG, abstração multi-LLM-provider
especulativa (Groq só entra quando uma etapa concreta precisar dele).

## Estrutura

```
pipeline/   Python — roda via GitHub Actions, nunca como servidor
  agents/{coletor,leitor_pdf,analista,scorer}/   um agente por responsabilidade
  graph/                                          LangGraph (só a partir da Fase 5)
  db/                                              cliente Supabase (upsert/busca pgvector)
  llm/                                             wrapper Gemini/Groq
  tests/{unit,fixtures}
  cli.py            entrypoint: roda com cwd=pipeline/ (`python cli.py demo`, `python cli.py investigar <ticker>`)
app/        Next.js (App Router) + Tailwind + shadcn/ui — só lê do Supabase e dispara workflow_dispatch
supabase/migrations/   schema versionado (pgvector)
```

`pipeline/` e `app/` são dois mundos isolados, unidos só pelo schema do
Supabase (pipeline escreve, app lê). Não criar um pacote `shared/` de tipos
cross-linguagem — isso é especulativo; Python e TypeScript nunca vão
compartilhar um tipo importável de verdade.

## Comandos

### pipeline/ (Python)
```bash
cd pipeline
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest                              # roda toda a suíte (cwd precisa ser pipeline/)
pytest tests/unit/test_health.py    # roda um arquivo específico
pytest -k nome_do_teste              # roda um teste específico por nome
```
Convenção de import: `pythonpath = ["."]` está configurado em
`pipeline/pyproject.toml`, então módulos são importados como
`agents.analista.contradicoes`, não `pipeline.agents...` (não há pacote
`pipeline` — o diretório `pipeline/` já é a raiz desse subprojeto).

### app/ (Next.js)
```bash
cd app
npm install
npm run dev     # servidor de desenvolvimento
npm run lint
npx tsc --noEmit
npm run build
```

## Regra de teste: nenhum teste de CI chama LLM real ou rede real

Toda função que chama o LLM recebe a chamada injetada (`llm_call`) — os testes
de contrato passam um fake e verificam que o prompt é montado e a resposta
estruturada é repassada sem corromper dados. Scrapers separam sempre
`fetch(url) -> html` de `parse(html) -> dado`, e o teste cobre só o `parse`
contra uma fixture HTML salva localmente. Validação com LLM/rede real
acontece uma vez, manualmente, ao fechar cada fase (skill `verify`) — nunca em
CI.

## Variáveis de ambiente

Ver `.env.example` na raiz. `SUPABASE_SERVICE_ROLE_KEY` e `GH_PAT` são
sempre server-side (GitHub Actions secrets / Vercel env vars não-`NEXT_PUBLIC_`)
— nunca expostas ao client. `GH_PAT` precisa do escopo `actions:write` (o
`GITHUB_TOKEN` automático do Actions não aciona `workflow_dispatch` de fora de
um workflow).

## Next.js 16 — atenção a breaking changes

`app/` usa Next.js 16.2.9, recente o suficiente para divergir do que está no
treinamento do modelo (App Router, convenções, etc. podem ter mudado). Antes
de escrever código novo em `app/`, checar `app/node_modules/next/dist/docs/`
ou o changelog oficial em vez de assumir comportamento de versões anteriores.

## Plugins/skills do Claude Code a usar neste repositório

Por convenção do usuário, sempre usar a skill já instalada em vez de
reimplementar o equivalente à mão: `code-review` e `simplify` em todo diff,
`verify` para confirmar comportamento real antes de fechar uma fase,
`security-review` em qualquer mudança que toque secrets, scraping ou conteúdo
não confiável indo para o LLM, `ui-ux-pro-max` para qualquer trabalho de
UI em `app/`, `review` para revisão de PRs.
