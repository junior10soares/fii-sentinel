from pathlib import Path

import pytest

from agents.leitor_pdf.extrator import extrair_texto

FIXTURE = Path("tests/fixtures/relatorio_exemplo.pdf")


def test_extrai_texto_de_pdf_fixture():
    paginas = extrair_texto(FIXTURE.read_bytes())

    assert len(paginas) == 2
    assert paginas[0].numero == 1
    assert "vacancia" in paginas[0].texto.lower()
    assert "vacancia" in paginas[1].texto.lower()


def test_pdf_invalido_levanta_erro_claro():
    with pytest.raises(ValueError):
        extrair_texto(b"isso nao e um pdf")
