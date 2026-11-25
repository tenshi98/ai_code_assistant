"""Rutas HTTP del servicio AI Code Generator & Debugger.

Expone la página de inicio y el endpoint ``/generate_code``. La comunicación con
Ollama se delega en :class:`server.services.ollama.OllamaClient`, inyectado
por FastAPI.
"""
import logging
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse

from server.config import get_settings
from server.dependencies import OllamaClientDep
from server.schemas.responses import CodeResponse
from server.services.ollama import (
    OllamaClient,
    OllamaRequestError,
    OllamaResponseError,
)

logger = logging.getLogger(__name__)

router = APIRouter()
"""Enrutador con los endpoints públicos del servicio."""


@router.get("/", response_class=FileResponse, summary="Sirve la interfaz web")
def serve_homepage() -> FileResponse:
    """Devuelve el archivo ``static/index.html``.

    :returns: Respuesta con el HTML de la aplicación.
    :rtype: fastapi.responses.FileResponse
    """
    settings = get_settings()
    return FileResponse(settings.static_dir / "index.html")


def _generate_text(client: OllamaClient, prompt: str, fallback: str) -> str:
    """Genera texto y traduce los errores de Ollama a errores HTTP 500.

    :param client: Cliente de Ollama inyectado por FastAPI.
    :type client: server.services.ollama.OllamaClient
    :param prompt: Instrucción completa para el modelo.
    :type prompt: str
    :param fallback: Texto de reserva si la respuesta no trae ``response``.
    :type fallback: str
    :returns: Texto generado por el modelo.
    :rtype: str
    :raises fastapi.HTTPException: Con estado 500 si Ollama no responde o
        devuelve un cuerpo inválido.
    """
    try:
        return client.generate(prompt, fallback)
    except OllamaRequestError as exc:
        logger.error("Fallo al contactar con Ollama: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Request to Ollama failed: {exc}",
        ) from exc
    except OllamaResponseError as exc:
        logger.error("Respuesta inválida de Ollama: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post(
    "/generate_code",
    response_model=CodeResponse,
    summary="Genera o depura código",
)
def generate_code(
    client: OllamaClientDep,
    prompt: Annotated[str, Form(description="Descripción del código o fragmento a depurar.")],
    mode: Annotated[str, Form(description="Modo de operación: 'generate' o 'debug'.")],
) -> CodeResponse:
    """Genera código nuevo o depura un fragmento existente.

    :param client: Cliente de Ollama inyectado por FastAPI.
    :type client: server.services.ollama.OllamaClient
    :param prompt: Descripción del código a generar o fragmento a depurar.
    :type prompt: str
    :param mode: ``"generate"`` para crear código, ``"debug"`` para corregirlo.
    :type mode: str
    :returns: Código generado o corregido por el modelo.
    :rtype: server.schemas.responses.CodeResponse
    :raises fastapi.HTTPException: ``400`` si el modo no es válido; ``500`` si
        la comunicación con Ollama falla.
    """
    # El prompt final depende del modo elegido por el usuario.
    if mode == "generate":
        full_prompt = f"Write a clean, well-documented {prompt} code snippet."
    elif mode == "debug":
        full_prompt = f"Debug and fix the following code:\n{prompt}"
    else:
        raise HTTPException(status_code=400, detail="Invalid mode selected.")

    generated = _generate_text(client, full_prompt, "No valid response received.")
    return CodeResponse(code=generated)
