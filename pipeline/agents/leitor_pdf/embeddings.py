from sentence_transformers import SentenceTransformer

MODELO_PADRAO = "paraphrase-multilingual-mpnet-base-v2"

_modelo: SentenceTransformer | None = None


def _carregar_modelo() -> SentenceTransformer:
    global _modelo
    if _modelo is None:
        _modelo = SentenceTransformer(MODELO_PADRAO)
    return _modelo


def gerar_embedding(texto: str) -> list[float]:
    return _carregar_modelo().encode(texto, normalize_embeddings=True).tolist()
