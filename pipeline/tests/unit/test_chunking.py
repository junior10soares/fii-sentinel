import pytest

from agents.leitor_pdf.chunking import chunkar


def test_chunk_preserva_todo_o_texto_sem_perda():
    texto = "texto longo " * 100
    chunks = chunkar(texto, tamanho=50, overlap=10)

    assert all(len(c) <= 50 for c in chunks)
    assert chunks[0] == texto[:50]
    assert texto.endswith(chunks[-1])


def test_chunks_consecutivos_se_sobrepoem_no_overlap():
    texto = "0123456789" * 10
    chunks = chunkar(texto, tamanho=30, overlap=10)

    assert chunks[0][-10:] == chunks[1][:10]


def test_overlap_maior_ou_igual_ao_tamanho_levanta_erro():
    with pytest.raises(ValueError):
        chunkar("qualquer texto", tamanho=10, overlap=10)


def test_tamanho_zero_ou_negativo_levanta_erro():
    with pytest.raises(ValueError):
        chunkar("qualquer texto", tamanho=0, overlap=0)


def test_overlap_negativo_levanta_erro():
    with pytest.raises(ValueError):
        chunkar("qualquer texto", tamanho=10, overlap=-1)
