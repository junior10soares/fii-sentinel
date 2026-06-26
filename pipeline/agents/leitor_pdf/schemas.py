from pydantic import BaseModel


class Pagina(BaseModel):
    numero: int
    texto: str
