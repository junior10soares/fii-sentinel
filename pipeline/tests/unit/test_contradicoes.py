from agents.analista.contradicoes import detectar_contradicoes
from agents.analista.schemas import Contradicao
from tests.fixtures.knri11_exemplo import NARRATIVA, SERIE_VACANCIA


def test_detecta_contradicao_vacancia_crescente():
    def llm_fake(prompt: str, schema: type) -> list[Contradicao]:
        assert schema is Contradicao
        assert "KNRI11" in prompt
        assert "6.3" in prompt
        return [
            Contradicao(
                trecho_relatorio=NARRATIVA,
                dado_contraditorio="vacância subiu 4 meses seguidos (4.2% -> 6.3%)",
                explicacao="O relatório afirma estabilização, mas a série mostra alta consecutiva.",
                severidade="alta",
            )
        ]

    resultado = detectar_contradicoes("KNRI11", NARRATIVA, SERIE_VACANCIA, llm_call=llm_fake)

    assert len(resultado) == 1
    assert resultado[0].severidade == "alta"


def test_sem_dado_nenhuma_contradicao():
    def llm_fake(prompt: str, schema: type) -> list[Contradicao]:
        return []

    resultado = detectar_contradicoes("KNRI11", NARRATIVA, SERIE_VACANCIA, llm_call=llm_fake)

    assert resultado == []
