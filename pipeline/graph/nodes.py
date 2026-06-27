import time
from typing import Callable

from agents.analista.schemas import Contradicao
from agents.coletor.schemas import IndicadoresFII
from agents.scorer.score import calcular_score
from agents.scorer.schemas import MarcoTimeline
from graph.state import InvestigacaoState

ColetorCall = Callable[[str], IndicadoresFII]
AnalistaCall = Callable[[str, str, list[dict]], list[Contradicao]]
TimelineCall = Callable[[str, list[dict], list[Contradicao], float], list[MarcoTimeline]]
ExtratorCall = Callable[[bytes], list]
ChunkerCall = Callable[[str, int, int], list[str]]
EmbedderCall = Callable[[str], list[float]]
InserirCall = Callable[..., None]
PersistirCall = Callable[..., None]

# Erros que reaparecer não resolve (ticker inexistente, layout da página mudou,
# robots.txt proíbe) — repetir só queima as tentativas. Só erro de rede
# (timeout, 5xx etc.) é transitório e vale tentar de novo.
ERROS_DEFINITIVOS = (ValueError, PermissionError)


def construir_no_coletor(coletor: ColetorCall, max_tentativas: int, intervalo_inicial: float = 1.0):
    def no(state: InvestigacaoState) -> dict:
        erros = list(state.get("erros", []))
        for tentativa in range(1, max_tentativas + 1):
            try:
                indicadores = coletor(state["ticker"])
                return {"indicadores": indicadores, "tentativas": tentativa}
            except ERROS_DEFINITIVOS as erro:
                erros.append(f"coletor (tentativa {tentativa}, erro definitivo): {erro}")
                return {"erros": erros, "tentativas": tentativa}
            except Exception as erro:
                erros.append(f"coletor (tentativa {tentativa}): {erro}")
                if tentativa < max_tentativas:
                    time.sleep(intervalo_inicial * 2 ** (tentativa - 1))
        return {"erros": erros, "tentativas": max_tentativas}

    return no


def rota_apos_coletor(state: InvestigacaoState) -> str:
    return "leitor_pdf" if state.get("indicadores") is not None else "falha"


def construir_no_leitor_pdf(
    extrator: ExtratorCall,
    chunker: ChunkerCall,
    embedder: EmbedderCall,
    inserir: InserirCall,
    tamanho_chunk: int = 500,
    overlap: int = 50,
):
    def no(state: InvestigacaoState) -> dict:
        pdf_bytes = state.get("pdf_bytes")
        if not pdf_bytes:
            return {"narrativa": "", "documentos_indexados": 0}

        paginas = extrator(pdf_bytes)
        texto_completo = "\n".join(p.texto for p in paginas)
        chunks = chunker(texto_completo, tamanho_chunk, overlap) if texto_completo else []

        erros = list(state.get("erros", []))
        indexados = 0
        for chunk in chunks:
            try:
                embedding = embedder(chunk)
                inserir(ticker=state["ticker"], fonte="relatorio_gerencial", conteudo=chunk, embedding=embedding)
                indexados += 1
            except Exception as erro:
                erros.append(f"leitor_pdf: falha ao indexar chunk: {erro}")

        return {"narrativa": texto_completo, "documentos_indexados": indexados, "erros": erros}

    return no


def construir_no_analista(analista: AnalistaCall):
    def no(state: InvestigacaoState) -> dict:
        try:
            contradicoes = analista(state["ticker"], state.get("narrativa", ""), state.get("serie_vacancia", []))
            return {"contradicoes": contradicoes}
        except Exception as erro:
            erros = list(state.get("erros", []))
            erros.append(f"analista: {erro}")
            return {"contradicoes": [], "erros": erros}

    return no


def no_scorer(state: InvestigacaoState) -> dict:
    score = calcular_score(
        state["indicadores"],
        state.get("contradicoes", []),
        state.get("serie_dy_historica"),
    )
    return {"score": score}


def construir_no_timeline(timeline: TimelineCall):
    def no(state: InvestigacaoState) -> dict:
        try:
            marcos = timeline(
                state["ticker"],
                state.get("serie_vacancia", []),
                state.get("contradicoes", []),
                state["score"].score_final,
            )
            return {"timeline": marcos}
        except Exception as erro:
            erros = list(state.get("erros", []))
            erros.append(f"timeline: {erro}")
            return {"timeline": [], "erros": erros}

    return no


def construir_no_falha(persistir: PersistirCall):
    def no(state: InvestigacaoState) -> dict:
        erros = list(state.get("erros", []))
        # status/persistido são campos separados de propósito: status descreve o
        # resultado da investigação, persistido descreve se isso de fato chegou
        # no Supabase — uma falha ao persistir não pode se disfarçar de sucesso.
        persistido = True
        try:
            persistir(ticker=state["ticker"], status="falha_coleta")
        except Exception as erro:
            persistido = False
            erros.append(f"persistir: {erro}")
        return {"status": "falha_coleta", "persistido": persistido, "erros": erros}

    return no


def construir_no_sucesso(persistir: PersistirCall):
    def no(state: InvestigacaoState) -> dict:
        erros = list(state.get("erros", []))
        score = state.get("score")
        persistido = True
        try:
            # montagem do resultado fica dentro do try: um item malformado em
            # `timeline` não pode crashar o grafo, só falhar a persistência
            # (mesma regra de "falha nunca se disfarça de sucesso" da Fase 5).
            resultado = score.model_dump() if score else None
            if resultado is not None:
                resultado["timeline"] = [marco.model_dump() for marco in state.get("timeline", [])]
                resultado["contradicoes"] = [c.model_dump() for c in state.get("contradicoes", [])]
            persistir(
                ticker=state["ticker"],
                status="concluida",
                score=score.score_final if score else None,
                resultado=resultado,
            )
        except Exception as erro:
            persistido = False
            erros.append(f"persistir: {erro}")
        return {"status": "concluida", "persistido": persistido, "erros": erros}

    return no
