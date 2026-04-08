from __future__ import annotations

import base64
from pathlib import Path

import requests


class LLMBrainError(RuntimeError):
    """Errores relacionados con Ollama o el modelo visual."""


class OllamaVisionBrain:
    """Consulta un modelo LLaVA local en Ollama con texto e imagen."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "llava",
        timeout_seconds: int = 90,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.endpoint = f"{self.base_url}/api/generate"

    def ask(self, question: str, image_path: str | Path) -> str:
        image_path = Path(image_path)
        if not image_path.exists():
            raise LLMBrainError(f"No se encontro la imagen temporal: {image_path}")

        payload = {
            "model": self.model_name,
            "prompt": (
                "Eres un asistente de videojuegos. "
                "Analiza la captura y responde en espanol. "
                "Se breve, directo y util para el jugador.\n\n"
                f"Pregunta: {question}"
            ),
            "images": [self._encode_image(image_path)],
            "stream": False,
            "options": {
                "temperature": 0.2,
            },
        }

        try:
            response = self.session.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise LLMBrainError(
                f"No fue posible consultar Ollama en {self.endpoint}: {exc}"
            ) from exc
        except ValueError as exc:
            raise LLMBrainError("Ollama devolvio una respuesta JSON invalida.") from exc

        answer = data.get("response", "").strip()
        if not answer:
            raise LLMBrainError("Ollama no devolvio texto en el campo 'response'.")

        return answer

    def _encode_image(self, image_path: Path) -> str:
        with image_path.open("rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
