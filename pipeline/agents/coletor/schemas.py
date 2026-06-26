from pydantic import BaseModel


class IndicadoresFII(BaseModel):
    ticker: str
    dy_12m: float
    preco_atual: float | None = None
    p_vp: float | None = None
    valor_patrimonial_cota: float | None = None
    liquidez_diaria: float | None = None
    numero_cotistas: int | None = None
