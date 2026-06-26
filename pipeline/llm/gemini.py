from google import genai
from pydantic import BaseModel

MODELO_PADRAO = "gemini-2.0-flash"


def gerar_estruturado(prompt: str, schema: type[BaseModel]) -> list[BaseModel]:
    """Chama o Gemini pedindo uma lista de `schema` como saída estruturada.

    Lê GEMINI_API_KEY do ambiente (via google.genai.Client default).
    """
    client = genai.Client()
    response = client.models.generate_content(
        model=MODELO_PADRAO,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": list[schema],
        },
    )
    return response.parsed
