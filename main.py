from __future__ import annotations

import logging
import os
from pathlib import Path

from audio_listener import AudioListener, AudioListenerError
from llm_brain import LLMBrainError, OllamaVisionBrain
from transcriber import Transcriber, TranscriberError
from tts_speaker import TTSSpeaker, TTSSpeakerError
from vision_capture import VisionCapture, VisionCaptureError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class GamingAssistantApp:
    """Orquesta el pipeline completo del asistente de videojuegos."""

    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parent
        self.temp_audio_path = self.base_dir / "temp_audio.wav"
        self.temp_capture_path = self.base_dir / "temp_capture.jpg"

        wake_word = os.getenv("WAKE_WORD", "sistema")
        vosk_model_path = os.getenv(
            "VOSK_MODEL_PATH",
            str(self.base_dir / "models" / "vosk-model-small-es-0.42"),
        )
        whisper_model_size = os.getenv("WHISPER_MODEL_SIZE", "medium")
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llava-phi3")
        edge_voice = os.getenv("EDGE_TTS_VOICE", "es-MX-DaliaNeural")

        self.listener = AudioListener(
            wake_word=wake_word,
            vosk_model_path=vosk_model_path,
        )
        self.transcriber = Transcriber(model_size=whisper_model_size)
        self.vision_capture = VisionCapture()
        self.brain = OllamaVisionBrain(
            base_url=ollama_url,
            model_name=ollama_model,
        )
        self.speaker = TTSSpeaker(voice=edge_voice)

    def run(self) -> None:
        logging.info("Asistente listo. Wake word: '%s'", self.listener.wake_word)
        logging.info("faster-whisper activo en: %s", self.transcriber.device)
        logging.info("Modelo visual de Ollama: %s", self.brain.model_name)
        while True:
            try:
                self._run_once()
            except KeyboardInterrupt:
                logging.info("Cierre solicitado por el usuario.")
                break
            except (
                AudioListenerError,
                VisionCaptureError,
                TranscriberError,
                LLMBrainError,
                TTSSpeakerError,
            ) as exc:
                logging.exception("Fallo en el ciclo actual: %s", exc)
                self._safe_speak("Hubo un error en el asistente. Intenta de nuevo.")
            except Exception as exc:
                logging.exception("Error no controlado: %s", exc)
                self._safe_speak("Ocurrio un error inesperado.")
            finally:
                self._cleanup_temp_files()

    def _run_once(self) -> None:
        logging.info("Esperando una nueva consulta...")
        self.listener.listen_for_command(
            output_path=self.temp_audio_path,
            on_wake_word_detected=self._capture_current_frame,
        )

        question = self.transcriber.transcribe(self.temp_audio_path)
        logging.info("Pregunta transcrita: %s", question)

        answer = self.brain.ask(question, self.temp_capture_path)
        logging.info("Respuesta generada por Ollama:")
        print(f"\n======== OLLAMA DICE ========\n{answer}\n=============================\n")

        self.speaker.speak(answer)

    def _capture_current_frame(self) -> None:
        self.vision_capture.capture(self.temp_capture_path)
        logging.info("Captura del juego guardada en %s", self.temp_capture_path.name)

    def _safe_speak(self, message: str) -> None:
        try:
            self.speaker.speak(message)
        except Exception:
            logging.error("No fue posible reproducir el mensaje de error.")

    def _cleanup_temp_files(self) -> None:
        self.temp_audio_path.unlink(missing_ok=True)
        self.temp_capture_path.unlink(missing_ok=True)


def main() -> None:
    app = GamingAssistantApp()
    app.run()


if __name__ == "__main__":
    main()
