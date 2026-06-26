import os

from pydantic import BaseModel
from supabase import Client, create_client

_cliente: Client | None = None


class DocumentoSimilar(BaseModel):
    id: str
    fonte: str
    conteudo: str
    metadata: dict
    similaridade: float


def _obter_cliente() -> Client:
    global _cliente
    if _cliente is None:
        _cliente = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    return _cliente


def inserir_documento(
    ticker: str,
    fonte: str,
    conteudo: str,
    embedding: list[float],
    metadata: dict | None = None,
) -> None:
    # ponytail: insert puro, sem dedup — a tabela não tem chave natural ainda.
    # Vira upsert de verdade quando um caller real (Fase 5+) deixar claro qual
    # é a chave de unicidade (provavelmente ticker+fonte+índice do chunk).
    _obter_cliente().table("documentos").insert(
        {
            "ticker": ticker,
            "fonte": fonte,
            "conteudo": conteudo,
            "embedding": embedding,
            "metadata": metadata or {},
        }
    ).execute()


def buscar_similares(ticker: str, query_embedding: list[float], k: int = 5) -> list[DocumentoSimilar]:
    resposta = _obter_cliente().rpc(
        "buscar_documentos_similares",
        {"p_ticker": ticker, "query_embedding": query_embedding, "match_count": k},
    ).execute()
    return [DocumentoSimilar(**linha) for linha in resposta.data]
