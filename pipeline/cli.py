import json
import sys
from functools import partial
from pathlib import Path

from agents.analista.contradicoes import detectar_contradicoes
from agents.coletor.status_invest import buscar_indicadores
from agents.scorer.score import calcular_score
from db.analises import salvar_analise
from graph.build import executar_grafo
from llm.gemini import gerar_estruturado

NARRATIVA_EXEMPLO = (
    "A gestão informa que a vacância física do portfólio segue em trajetória "
    "de estabilização, com perspectiva de melhora gradual nos próximos meses."
)

SERIE_VACANCIA_EXEMPLO = [
    {"mes": "2024-01", "vacancia": 4.2},
    {"mes": "2024-02", "vacancia": 5.1},
    {"mes": "2024-03", "vacancia": 5.8},
    {"mes": "2024-04", "vacancia": 6.3},
]


def demo() -> None:
    contradicoes = detectar_contradicoes(
        ticker="KNRI11",
        narrativa=NARRATIVA_EXEMPLO,
        serie_historica=SERIE_VACANCIA_EXEMPLO,
        llm_call=gerar_estruturado,
    )
    if not contradicoes:
        print("Nenhuma contradição encontrada.")
        return
    for c in contradicoes:
        print(f"[{c.severidade.upper()}] {c.dado_contraditorio}\n  -> {c.explicacao}\n")


def indicadores(ticker: str) -> None:
    print(buscar_indicadores(ticker).model_dump_json(indent=2))


def score(ticker: str) -> None:
    # ponytail: sem contradições reais (precisaria de narrativa + LLM de um
    # relatório de verdade) nem série histórica de DY (a Fase 2 só coleta o
    # instantâneo atual) — "transparência" e "tendência" ficam sempre no valor
    # neutro/máximo aqui; o score reflete só os indicadores do coletor.
    indicadores_reais = buscar_indicadores(ticker)
    resultado = calcular_score(indicadores_reais, contradicoes=[])
    print(resultado.model_dump_json(indent=2))


def investigar(ticker: str) -> None:
    # ponytail: sem coletor de relatório PDF real nem série de DY histórica
    # ainda — usa o mesmo fixture da Fase 3 como "relatório" e a mesma série de
    # vacância demo da Fase 1. Troca quando esses scrapers reais existirem; o
    # grafo em si não muda, só os dados de entrada.
    pdf_bytes = (Path(__file__).parent / "tests/fixtures/relatorio_exemplo.pdf").read_bytes()
    resultado = executar_grafo(
        {"ticker": ticker.upper(), "pdf_bytes": pdf_bytes, "serie_vacancia": SERIE_VACANCIA_EXEMPLO},
        coletor=buscar_indicadores,
        analista=partial(detectar_contradicoes, llm_call=gerar_estruturado),
        persistir=salvar_analise,
    )
    saida = {
        "ticker": resultado.get("ticker"),
        "status": resultado.get("status"),
        "persistido": resultado.get("persistido"),
        "tentativas": resultado.get("tentativas"),
        "indicadores": resultado["indicadores"].model_dump() if resultado.get("indicadores") else None,
        "contradicoes": [c.model_dump() for c in resultado.get("contradicoes", [])],
        "score": resultado["score"].model_dump() if resultado.get("score") else None,
        "documentos_indexados": resultado.get("documentos_indexados"),
        "erros": resultado.get("erros", []),
    }
    print(json.dumps(saida, indent=2, ensure_ascii=False))


COMANDOS = {"demo": demo, "indicadores": indicadores, "score": score, "investigar": investigar}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        print(f"Uso: python cli.py [{'|'.join(COMANDOS)}] [args]")
        sys.exit(1)
    COMANDOS[sys.argv[1]](*sys.argv[2:])


if __name__ == "__main__":
    main()
