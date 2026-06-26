# FII Sentinel

Investigador autônomo de Fundos de Investimento Imobiliário (FIIs). Não é um
dashboard de métricas — ele compara o discurso do relatório gerencial com os
números reais e aponta contradições: *"a gestora disse que a vacância estava
estabilizando, mas os dados mostram alta pelo 3º mês consecutivo."*

> 🚧 Em desenvolvimento. Status e arquitetura completos em [CLAUDE.md](./CLAUDE.md).

## O que faz

Dado um ticker (ex: `KNRI11`):
1. Raspa dados públicos (DY, vacância, P/VP, FFO, número de cotistas).
2. Indexa os relatórios gerenciais (PDF) dos últimos 12 meses para RAG.
3. Cruza o texto dos relatórios com os números via LLM e aponta contradições.
4. Gera um score de saúde financeira 0-100, com justificativa por critério.
5. Monta uma linha do tempo com contexto narrativo gerado por IA.

## Stack

| Camada | Escolha |
|---|---|
| Pipeline (scraping, PDF, embeddings, orquestração) | Python + LangGraph, roda via GitHub Actions |
| LLM | Gemini (Google AI Studio), Groq como alternativa |
| Banco vetorial + relacional | Supabase Postgres + pgvector |
| Frontend | Next.js + Tailwind + shadcn/ui, deploy na Vercel |

Decisões de stack e por quê estão documentadas em [CLAUDE.md](./CLAUDE.md).

## Estrutura

```
pipeline/   Python — agentes (coletor, leitor_pdf, analista, scorer), grafo LangGraph
app/        Next.js — frontend, lê do Supabase e dispara investigações sob demanda
supabase/   schema versionado (migrations)
```

## Desenvolvimento local

```bash
# pipeline
cd pipeline && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest

# app
cd app && npm install && npm run dev
```

## Licença

MIT — ver [LICENSE](./LICENSE).
