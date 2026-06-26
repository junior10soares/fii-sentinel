from pydantic import BaseModel


class CriterioScore(BaseModel):
    nome: str
    peso: float
    pontos: float
    justificativa: str


class ScoreResult(BaseModel):
    ticker: str
    score_final: float
    criterios: list[CriterioScore]


class MarcoTimeline(BaseModel):
    periodo: str
    narrativa: str
