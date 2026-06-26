from langgraph.graph import END, START, StateGraph

from agents.leitor_pdf.chunking import chunkar
from agents.leitor_pdf.embeddings import gerar_embedding
from agents.leitor_pdf.extrator import extrair_texto
from db.documentos import inserir_documento
from graph.nodes import (
    AnalistaCall,
    ColetorCall,
    PersistirCall,
    TimelineCall,
    construir_no_analista,
    construir_no_coletor,
    construir_no_falha,
    construir_no_leitor_pdf,
    construir_no_sucesso,
    construir_no_timeline,
    no_scorer,
    rota_apos_coletor,
)
from graph.state import InvestigacaoState


def construir_grafo(
    coletor: ColetorCall,
    analista: AnalistaCall,
    timeline: TimelineCall,
    persistir: PersistirCall,
    extrator=extrair_texto,
    chunker=chunkar,
    embedder=gerar_embedding,
    inserir=inserir_documento,
    max_tentativas: int = 3,
    intervalo_inicial: float = 1.0,
):
    grafo = StateGraph(InvestigacaoState)
    grafo.add_node("coletor", construir_no_coletor(coletor, max_tentativas, intervalo_inicial))
    grafo.add_node("leitor_pdf", construir_no_leitor_pdf(extrator, chunker, embedder, inserir))
    grafo.add_node("analista", construir_no_analista(analista))
    grafo.add_node("scorer", no_scorer)
    grafo.add_node("timeline", construir_no_timeline(timeline))
    grafo.add_node("falha", construir_no_falha(persistir))
    grafo.add_node("sucesso", construir_no_sucesso(persistir))

    grafo.add_edge(START, "coletor")
    grafo.add_conditional_edges("coletor", rota_apos_coletor, {"falha": "falha", "leitor_pdf": "leitor_pdf"})
    grafo.add_edge("leitor_pdf", "analista")
    grafo.add_edge("analista", "scorer")
    grafo.add_edge("scorer", "timeline")
    grafo.add_edge("timeline", "sucesso")
    grafo.add_edge("falha", END)
    grafo.add_edge("sucesso", END)

    return grafo.compile()


def executar_grafo(state: dict, **kwargs) -> InvestigacaoState:
    return construir_grafo(**kwargs).invoke(state)
