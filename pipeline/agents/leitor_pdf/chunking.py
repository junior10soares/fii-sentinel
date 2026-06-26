def chunkar(texto: str, tamanho: int, overlap: int) -> list[str]:
    if tamanho <= 0:
        raise ValueError("tamanho precisa ser maior que zero")
    if overlap < 0:
        raise ValueError("overlap não pode ser negativo")
    if overlap >= tamanho:
        raise ValueError("overlap precisa ser menor que tamanho")
    passo = tamanho - overlap
    return [texto[i : i + tamanho] for i in range(0, len(texto), passo)]
