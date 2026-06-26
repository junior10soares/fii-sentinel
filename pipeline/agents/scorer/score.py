from agents.analista.schemas import Contradicao
from agents.coletor.schemas import IndicadoresFII
from agents.scorer.schemas import CriterioScore, ScoreResult

PESO_DIVIDENDOS = 0.25
PESO_ATIVOS = 0.20
PESO_TRANSPARENCIA = 0.20
PESO_SAUDE_FINANCEIRA = 0.20
PESO_TENDENCIA = 0.15

PENALIDADE_POR_SEVERIDADE = {"alta": 30, "media": 15, "baixa": 5}

DY_ESCALA = 10.0  # fator que mapeia 0-10% de DY para 0-100 pontos
PVP_REFERENCIA = 1.0  # P/VP <= isso = nota máxima (cota negociada ao valor patrimonial ou abaixo)
LIQUIDEZ_REFERENCIA = 500_000.0  # R$/dia considerado saudável para um FII


def _criterio_dividendos(indicadores: IndicadoresFII) -> CriterioScore:
    pontos = min(100.0, max(0.0, indicadores.dy_12m * DY_ESCALA))
    return CriterioScore(
        nome="dividendos",
        peso=PESO_DIVIDENDOS,
        pontos=pontos,
        justificativa=f"DY de {indicadores.dy_12m:.2f}%: {pontos:.0f} pontos",
    )


def _criterio_ativos(indicadores: IndicadoresFII) -> CriterioScore:
    if indicadores.p_vp is None:
        return CriterioScore(
            nome="ativos", peso=PESO_ATIVOS, pontos=50.0,
            justificativa="P/VP não disponível: 50 pontos (neutro)",
        )
    if indicadores.p_vp <= 0:
        return CriterioScore(
            nome="ativos", peso=PESO_ATIVOS, pontos=0.0,
            justificativa=f"P/VP de {indicadores.p_vp:.2f} (valor patrimonial nulo ou negativo): 0 pontos",
        )
    pontos = 100.0 if indicadores.p_vp <= PVP_REFERENCIA else max(0.0, 100.0 - (indicadores.p_vp - PVP_REFERENCIA) * 100.0)
    return CriterioScore(
        nome="ativos", peso=PESO_ATIVOS, pontos=pontos,
        justificativa=f"P/VP de {indicadores.p_vp:.2f}: {pontos:.0f} pontos",
    )


def _criterio_transparencia(contradicoes: list[Contradicao]) -> CriterioScore:
    deducao = sum(PENALIDADE_POR_SEVERIDADE[c.severidade] for c in contradicoes)
    pontos = max(0.0, 100.0 - deducao)
    if contradicoes:
        justificativa = f"{len(contradicoes)} contradição(ões) encontrada(s): -{deducao} pontos"
    else:
        justificativa = "Nenhuma contradição encontrada: 100 pontos"
    return CriterioScore(nome="transparencia", peso=PESO_TRANSPARENCIA, pontos=pontos, justificativa=justificativa)


def _criterio_saude_financeira(indicadores: IndicadoresFII) -> CriterioScore:
    if indicadores.liquidez_diaria is None:
        return CriterioScore(
            nome="saude_financeira", peso=PESO_SAUDE_FINANCEIRA, pontos=50.0,
            justificativa="Liquidez não disponível: 50 pontos (neutro)",
        )
    pontos = min(100.0, max(0.0, indicadores.liquidez_diaria / LIQUIDEZ_REFERENCIA * 100.0))
    return CriterioScore(
        nome="saude_financeira", peso=PESO_SAUDE_FINANCEIRA, pontos=pontos,
        justificativa=f"Liquidez diária de R$ {indicadores.liquidez_diaria:.2f}: {pontos:.0f} pontos",
    )


def _criterio_tendencia(serie_dy_historica: list[float] | None) -> CriterioScore:
    # ponytail: compara só ponta a ponta (primeiro vs último), ignora o caminho no
    # meio — upgrade pra média das variações (ou regressão linear) se isso causar
    # um veredito errado na prática com dado histórico real.
    if not serie_dy_historica or len(serie_dy_historica) < 2:
        return CriterioScore(
            nome="tendencia", peso=PESO_TENDENCIA, pontos=50.0,
            justificativa="Sem série histórica suficiente para avaliar tendência: 50 pontos (neutro)",
        )
    delta = serie_dy_historica[-1] - serie_dy_historica[0]
    if delta > 0:
        pontos, direcao = 100.0, "alta"
    elif delta < 0:
        pontos, direcao = 0.0, "queda"
    else:
        pontos, direcao = 50.0, "estável"
    justificativa = (
        f"DY foi de {serie_dy_historica[0]:.2f}% para {serie_dy_historica[-1]:.2f}% "
        f"({direcao}): {pontos:.0f} pontos"
    )
    return CriterioScore(nome="tendencia", peso=PESO_TENDENCIA, pontos=pontos, justificativa=justificativa)


def calcular_score(
    indicadores: IndicadoresFII,
    contradicoes: list[Contradicao],
    serie_dy_historica: list[float] | None = None,
) -> ScoreResult:
    criterios = [
        _criterio_dividendos(indicadores),
        _criterio_ativos(indicadores),
        _criterio_transparencia(contradicoes),
        _criterio_saude_financeira(indicadores),
        _criterio_tendencia(serie_dy_historica),
    ]
    score_final = sum(c.peso * c.pontos for c in criterios)
    return ScoreResult(ticker=indicadores.ticker, score_final=score_final, criterios=criterios)
