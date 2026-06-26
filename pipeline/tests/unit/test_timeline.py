from agents.analista.schemas import Contradicao
from agents.scorer.schemas import MarcoTimeline
from agents.scorer.timeline import gerar_timeline
from tests.fixtures.knri11_exemplo import SERIE_VACANCIA


def test_gera_um_marco_por_periodo_da_serie():
    def llm_fake(prompt: str, schema: type) -> list[MarcoTimeline]:
        assert schema is MarcoTimeline
        assert "KNRI11" in prompt
        assert "76.0" in prompt
        return [MarcoTimeline(periodo=ponto["mes"], narrativa="...") for ponto in SERIE_VACANCIA]

    resultado = gerar_timeline("KNRI11", SERIE_VACANCIA, contradicoes=[], score_final=76.0, llm_call=llm_fake)

    assert len(resultado) == len(SERIE_VACANCIA)


def test_inclui_contradicoes_no_prompt_quando_existem():
    contradicao = Contradicao(
        trecho_relatorio="...",
        dado_contraditorio="vacância subiu 4 meses seguidos",
        explicacao="...",
        severidade="alta",
    )

    def llm_fake(prompt: str, schema: type) -> list[MarcoTimeline]:
        assert "vacância subiu 4 meses seguidos" in prompt
        return []

    gerar_timeline("KNRI11", SERIE_VACANCIA, contradicoes=[contradicao], score_final=76.0, llm_call=llm_fake)


def test_sem_serie_historica_nao_chama_llm():
    def llm_fake(prompt: str, schema: type) -> list[MarcoTimeline]:
        raise AssertionError("não deveria chamar o LLM sem série histórica")

    resultado = gerar_timeline("KNRI11", [], contradicoes=[], score_final=76.0, llm_call=llm_fake)

    assert resultado == []
