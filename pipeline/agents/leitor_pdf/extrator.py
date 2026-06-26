import fitz

from agents.leitor_pdf.schemas import Pagina


def extrair_texto(pdf_bytes: bytes) -> list[Pagina]:
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as documento:
            return [Pagina(numero=i + 1, texto=pagina.get_text()) for i, pagina in enumerate(documento)]
    except fitz.FileDataError as erro:
        raise ValueError(f"PDF inválido ou corrompido: {erro}") from erro
