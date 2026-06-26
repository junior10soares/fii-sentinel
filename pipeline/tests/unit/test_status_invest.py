from pathlib import Path

import pytest

from agents.coletor.status_invest import parse_indicadores

FIXTURE = Path("tests/fixtures/status_invest_knri11.html")


def test_parse_indicadores_de_html_fixture():
    indicadores = parse_indicadores(FIXTURE.read_text(encoding="utf-8"))

    assert indicadores.ticker == "KNRI11"
    assert indicadores.dy_12m == 8.38
    assert indicadores.p_vp == 0.92
    assert indicadores.valor_patrimonial_cota == 163.15
    assert indicadores.liquidez_diaria == 6581450.48
    assert indicadores.numero_cotistas == 313130
    assert indicadores.preco_atual == 149.45


def test_levanta_erro_sem_data_ticker():
    with pytest.raises(ValueError):
        parse_indicadores("<html><body>sem dados</body></html>")
