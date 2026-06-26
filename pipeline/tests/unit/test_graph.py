from agents.analista.schemas import Contradicao
from agents.coletor.schemas import IndicadoresFII
from agents.scorer.schemas import MarcoTimeline
from graph.build import executar_grafo


def _timeline_vazia(ticker, serie, contradicoes, score_final):
    return []


def _coletor_que_sempre_falha(ticker: str) -> IndicadoresFII:
    raise RuntimeError(f"erro transitório de rede para {ticker}")


def _coletor_com_erro_definitivo(ticker: str) -> IndicadoresFII:
    raise ValueError(f"ticker inexistente: {ticker}")


def test_grafo_persiste_status_falha_quando_coletor_esgota_tentativas():
    persistidos = []

    resultado = executar_grafo(
        {"ticker": "FAKE11"},
        coletor=_coletor_que_sempre_falha,
        analista=lambda ticker, narrativa, serie: [],
        timeline=_timeline_vazia,
        persistir=lambda **kwargs: persistidos.append(kwargs),
        max_tentativas=3,
        intervalo_inicial=0,
    )

    assert resultado["status"] == "falha_coleta"
    assert resultado["tentativas"] == 3
    assert resultado["persistido"] is True
    assert persistidos == [{"ticker": "FAKE11", "status": "falha_coleta"}]


def test_grafo_nao_repete_tentativa_em_erro_definitivo():
    resultado = executar_grafo(
        {"ticker": "FAKE11"},
        coletor=_coletor_com_erro_definitivo,
        analista=lambda ticker, narrativa, serie: [],
        timeline=_timeline_vazia,
        persistir=lambda **kwargs: None,
        max_tentativas=3,
        intervalo_inicial=0,
    )

    assert resultado["status"] == "falha_coleta"
    assert resultado["tentativas"] == 1


def test_grafo_reporta_persistido_falso_quando_supabase_falha():
    def persistir_que_falha(**kwargs):
        raise ConnectionError("Supabase indisponível")

    resultado = executar_grafo(
        {"ticker": "FAKE11"},
        coletor=_coletor_que_sempre_falha,
        analista=lambda ticker, narrativa, serie: [],
        timeline=_timeline_vazia,
        persistir=persistir_que_falha,
        max_tentativas=1,
        intervalo_inicial=0,
    )

    assert resultado["status"] == "falha_coleta"
    assert resultado["persistido"] is False
    assert any("persistir" in erro for erro in resultado["erros"])


def test_grafo_completa_com_sucesso_e_calcula_score():
    indicadores = IndicadoresFII(ticker="KNRI11", dy_12m=10.0, p_vp=1.0, liquidez_diaria=500_000.0)
    contradicao = Contradicao(
        trecho_relatorio="...",
        dado_contraditorio="...",
        explicacao="...",
        severidade="baixa",
    )
    marco = MarcoTimeline(periodo="2024-04", narrativa="vacância subiu")
    persistidos = []

    resultado = executar_grafo(
        {"ticker": "KNRI11"},
        coletor=lambda ticker: indicadores,
        analista=lambda ticker, narrativa, serie: [contradicao],
        timeline=lambda ticker, serie, contradicoes, score_final: [marco],
        persistir=lambda **kwargs: persistidos.append(kwargs),
    )

    assert resultado["status"] == "concluida"
    assert resultado["tentativas"] == 1
    assert resultado["score"].ticker == "KNRI11"
    assert resultado["timeline"] == [marco]
    assert resultado["documentos_indexados"] == 0
    assert len(persistidos) == 1
    assert persistidos[0]["status"] == "concluida"
    assert persistidos[0]["score"] == resultado["score"].score_final
    assert persistidos[0]["resultado"]["timeline"] == [marco.model_dump()]


def test_grafo_indexa_documentos_quando_ha_pdf():
    indicadores = IndicadoresFII(ticker="KNRI11", dy_12m=10.0)
    chunks_inseridos = []

    resultado = executar_grafo(
        {"ticker": "KNRI11", "pdf_bytes": b"qualquer coisa"},
        coletor=lambda ticker: indicadores,
        analista=lambda ticker, narrativa, serie: [],
        timeline=_timeline_vazia,
        persistir=lambda **kwargs: None,
        extrator=lambda pdf_bytes: [type("Pagina", (), {"texto": "vacancia subiu 3 meses"})()],
        chunker=lambda texto, tamanho, overlap: [texto],
        embedder=lambda chunk: [0.1, 0.2],
        inserir=lambda **kwargs: chunks_inseridos.append(kwargs),
    )

    assert resultado["narrativa"] == "vacancia subiu 3 meses"
    assert resultado["documentos_indexados"] == 1
    assert chunks_inseridos == [
        {"ticker": "KNRI11", "fonte": "relatorio_gerencial", "conteudo": "vacancia subiu 3 meses", "embedding": [0.1, 0.2]}
    ]


def test_grafo_degrada_graciosamente_quando_timeline_falha():
    indicadores = IndicadoresFII(ticker="KNRI11", dy_12m=10.0)

    def timeline_que_falha(ticker, serie, contradicoes, score_final):
        raise RuntimeError("Gemini indisponível")

    resultado = executar_grafo(
        {"ticker": "KNRI11"},
        coletor=lambda ticker: indicadores,
        analista=lambda ticker, narrativa, serie: [],
        timeline=timeline_que_falha,
        persistir=lambda **kwargs: None,
    )

    assert resultado["status"] == "concluida"
    assert resultado["timeline"] == []
    assert any("timeline" in erro for erro in resultado["erros"])
