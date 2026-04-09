from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import edge_tts
import pygame


class TTSSpeakerError(RuntimeError):
    """Errores relacionados con la sintesis o reproduccion de voz."""


class TTSSpeaker:
    """Convierte texto a voz con edge-tts y reproduce el audio localmente."""

    def __init__(
        self,
        voice: str = "es-MX-DaliaNeural",
        rate: str = "+0%",
        volume: str = "+0%",
    ) -> None:
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self._mixer_ready = False

    def speak(self, text: str) -> None:
        text = text.strip()
        if not text:
            return

        temp_file = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name)
        try:
            self._synthesize_to_file(text, temp_file)
            self._play_audio(temp_file)
        except Exception as exc:
            if isinstance(exc, TTSSpeakerError):
                raise
            raise TTSSpeakerError(f"Error al reproducir la respuesta por voz: {exc}") from exc
        finally:
            try:
                if self._mixer_ready:
                    try:
                        pygame.mixer.music.unload()
                    except pygame.error:
                        pass
                temp_file.unlink(missing_ok=True)
            except OSError:
                pass

    def _synthesize_to_file(self, text: str, output_path: Path) -> None:
        async def _runner() -> None:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    communicate = edge_tts.Communicate(
                        text=text,
                        voice=self.voice,
                        rate=self.rate,
                        volume=self.volume,
                    )
                    await communicate.save(str(output_path))
                    break  # Exito! Salimos del loop
                except Exception:
                    if attempt == max_retries - 1:
                        raise  # Si fue el ultimo intento, levantamos el error original
                    await asyncio.sleep(1.0) # Esperamos poquito antes de reintentar

        try:
            asyncio.run(_runner())
        except RuntimeError:
            # Fallback util si el codigo se integra luego dentro de otro event loop.
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(_runner())
            finally:
                loop.close()

    def _play_audio(self, audio_path: Path) -> None:
        self._ensure_mixer()
        try:
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
        except pygame.error as exc:
            raise TTSSpeakerError(
                f"No fue posible cargar o reproducir el audio: {exc}"
            ) from exc

        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            clock.tick(20)

    def _ensure_mixer(self) -> None:
        if self._mixer_ready:
            return

        try:
            pygame.mixer.init()
            self._mixer_ready = True
        except pygame.error as exc:
            raise TTSSpeakerError(
                f"No fue posible inicializar el dispositivo de audio: {exc}"
            ) from exc
