from db._cliente import obter_cliente


def salvar_analise(
    ticker: str,
    status: str,
    score: float | None = None,
    resultado: dict | None = None,
) -> None:
    cliente = obter_cliente()
    # analises.ticker tem FK pra fiis(ticker) — garante o fii antes de inserir.
    # ponytail: só grava o ticker, sem nome — o coletor não extrai o nome do
    # fundo ainda. Resolve quando isso passar a importar pro frontend (Fase 8).
    cliente.table("fiis").upsert({"ticker": ticker}, on_conflict="ticker").execute()
    cliente.table("analises").insert(
        {"ticker": ticker, "status": status, "score": score, "resultado": resultado}
    ).execute()
