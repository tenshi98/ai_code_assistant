"""Modelo de respuesta del generador y depurador de código."""
from pydantic import BaseModel, Field


class CodeResponse(BaseModel):
    """Código generado o corregido por el modelo."""

    code: str = Field(..., description="Código generado o corregido por Ollama.")
