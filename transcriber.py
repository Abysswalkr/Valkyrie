from __future__ import annotations

from pathlib import Path

from faster_whisper import WhisperModel


class TranscriberError(RuntimeError):
    """Errores relacionados con la transcripcion."""


class Transcriber:
    """Transcribe audio con faster-whisper, priorizando CUDA."""

    def __init__(
        self,
        model_size: str = "medium",
        language: str = "es",
        beam_size: int = 1,
    ) -> None:
        self.model_size = model_size
        self.language = language
        self.beam_size = beam_size
        self.model, self.device = self._load_model()

    def _load_model(self) -> tuple[WhisperModel, str]:
        try:
            model = WhisperModel(
                self.model_size,
                device="cuda",
                compute_type="float16",
            )
            return model, "cuda"
        except Exception:
            # Fallback para no bloquear todo el asistente si CUDA no esta listo.
            model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",
            )
            return model, "cpu"

    def transcribe(self, audio_path: str | Path) -> str:
        audio_path = Path(audio_path)
        try:
            segments, _ = self.model.transcribe(
                str(audio_path),
                language=self.language,
                beam_size=self.beam_size,
                best_of=1,
                vad_filter=True,
                condition_on_previous_text=False,
            )

            transcript = " ".join(
                segment.text.strip() for segment in segments if segment.text.strip()
            ).strip()

            if not transcript:
                raise TranscriberError(
                    "La transcripcion termino sin texto util."
                )

            return transcript
        except Exception as exc:
            if isinstance(exc, TranscriberError):
                raise
            raise TranscriberError(
                f"Error al transcribir el audio con faster-whisper: {exc}"
            ) from exc
        finally:
            audio_path.unlink(missing_ok=True)
