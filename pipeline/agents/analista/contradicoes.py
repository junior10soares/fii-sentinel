from typing import Callable

from agents.analista.schemas import Contradicao

LlmCall = Callable[[str, type[Contradicao]], list[Contradicao]]

PROMPT_TEMPLATE = """Você é um analista financeiro especializado em FIIs (fundos imobiliários) \
brasileiros. Sua tarefa é apontar contradições entre o discurso de um relatório \
gerencial e os números reais do fundo.

Ticker: {ticker}

Trecho do relatório gerencial:
\"\"\"
{narrativa}
\"\"\"

Série histórica real do indicador citado no trecho:
{serie_formatada}

Aponte contradições entre o que o texto afirma e o que a série histórica mostra. \
Considere apenas o que está nos dados fornecidos, não invente números. Se não houver \
contradição, retorne uma lista vazia."""


def _formatar_serie(serie_historica: list[dict]) -> str:
    return "\n".join(f"- {ponto['mes']}: {ponto['vacancia']}%" for ponto in serie_historica)


def detectar_contradicoes(
    ticker: str,
    narrativa: str,
    serie_historica: list[dict],
    llm_call: LlmCall,
) -> list[Contradicao]:
    prompt = PROMPT_TEMPLATE.format(
        ticker=ticker,
        narrativa=narrativa,
        serie_formatada=_formatar_serie(serie_historica),
    )
    return llm_call(prompt, Contradicao)
