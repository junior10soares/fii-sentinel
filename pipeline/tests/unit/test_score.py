import pytest

from agents.analista.schemas import Contradicao
from agents.coletor.schemas import IndicadoresFII
from agents.scorer.score import calcular_score

INDICADORES_BASE = IndicadoresFII(ticker="KNRI11", dy_12m=10.0, p_vp=1.0, liquidez_diaria=500_000.0)


def test_score_pondera_corretamente_os_5_criterios():
    resultado = calcular_score(INDICADORES_BASE, contradicoes=[])

    assert resultado.ticker == "KNRI11"
    assert len(resultado.criterios) == 5
    assert sum(c.peso for c in resultado.criterios) == pytest.approx(1.0)
    assert resultado.score_final == pytest.approx(92.5)


def test_contradicao_severa_reduz_nota_transparencia():
    contradicao_alta = Contradicao(
        trecho_relatorio="...",
        dado_contraditorio="...",
        explicacao="...",
        severidade="alta",
    )

    sem_contradicao = calcular_score(INDICADORES_BASE, contradicoes=[])
    com_contradicao = calcular_score(INDICADORES_BASE, contradicoes=[contradicao_alta])

    assert com_contradicao.score_final < sem_contradicao.score_final
    assert sem_contradicao.score_final - com_contradicao.score_final == pytest.approx(6.0)


def test_tendencia_de_alta_no_dy_aumenta_score():
    sem_serie = calcular_score(INDICADORES_BASE, contradicoes=[])
    com_serie_alta = calcular_score(INDICADORES_BASE, contradicoes=[], serie_dy_historica=[8.0, 9.0, 10.0])

    assert com_serie_alta.score_final > sem_serie.score_final


def test_indicador_ausente_usa_pontuacao_neutra():
    indicadores_incompletos = IndicadoresFII(ticker="KNRI11", dy_12m=10.0)
    resultado = calcular_score(indicadores_incompletos, contradicoes=[])

    criterio_ativos = next(c for c in resultado.criterios if c.nome == "ativos")
    assert criterio_ativos.pontos == 50.0


def test_pvp_negativo_zera_nota_de_ativos():
    indicadores_distress = IndicadoresFII(ticker="KNRI11", dy_12m=10.0, p_vp=-0.5)
    resultado = calcular_score(indicadores_distress, contradicoes=[])

    criterio_ativos = next(c for c in resultado.criterios if c.nome == "ativos")
    assert criterio_ativos.pontos == 0.0
