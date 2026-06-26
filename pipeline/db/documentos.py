from pydantic import BaseModel

from db._cliente import obter_cliente


class DocumentoSimilar(BaseModel):
    id: str
    fonte: str
    conteudo: str
    metadata: dict
    similaridade: float


def inserir_documento(
    ticker: str,
    fonte: str,
    conteudo: str,
    embedding: list[float],
    metadata: dict | None = None,
) -> None:
    # ponytail: insert puro, sem dedup — a tabela não tem chave natural ainda.
    # Vira upsert de verdade quando o caller (o grafo, desde a Fase 5) deixar
    # claro qual é a chave de unicidade (provavelmente ticker+fonte+índice do chunk).
    obter_cliente().table("documentos").insert(
        {
            "ticker": ticker,
            "fonte": fonte,
            "conteudo": conteudo,
            "embedding": embedding,
            "metadata": metadata or {},
        }
    ).execute()


def buscar_similares(ticker: str, query_embedding: list[float], k: int = 5) -> list[DocumentoSimilar]:
    resposta = obter_cliente().rpc(
        "buscar_documentos_similares",
        {"p_ticker": ticker, "query_embedding": query_embedding, "match_count": k},
    ).execute()
    return [DocumentoSimilar(**linha) for linha in resposta.data]
