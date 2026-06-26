from typing import Literal

from pydantic import BaseModel


class Contradicao(BaseModel):
    trecho_relatorio: str
    dado_contraditorio: str
    explicacao: str
    severidade: Literal["baixa", "media", "alta"]
