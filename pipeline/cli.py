import sys

from agents.analista.contradicoes import detectar_contradicoes
from agents.coletor.status_invest import buscar_indicadores
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


COMANDOS = {"demo": demo, "indicadores": indicadores}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        print(f"Uso: python cli.py [{'|'.join(COMANDOS)}] [args]")
        sys.exit(1)
    COMANDOS[sys.argv[1]](*sys.argv[2:])


if __name__ == "__main__":
    main()
