from typing import TypedDict

from agents.analista.schemas import Contradicao
from agents.coletor.schemas import IndicadoresFII
from agents.scorer.schemas import MarcoTimeline, ScoreResult


class InvestigacaoState(TypedDict, total=False):
    ticker: str
    pdf_bytes: bytes
    serie_vacancia: list[dict]
    serie_dy_historica: list[float]
    indicadores: IndicadoresFII | None
    narrativa: str
    documentos_indexados: int
    contradicoes: list[Contradicao]
    score: ScoreResult | None
    timeline: list[MarcoTimeline]
    status: str
    persistido: bool
    erros: list[str]
    tentativas: int
