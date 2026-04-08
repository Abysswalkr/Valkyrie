from __future__ import annotations

import audioop
import json
import queue
import re
import time
import wave
from collections import deque
from pathlib import Path
from typing import Callable

import sounddevice as sd
from vosk import KaldiRecognizer, Model


class AudioListenerError(RuntimeError):
    """Errores relacionados con la captura de audio y wake word."""


class AudioListener:
    """Escucha el microfono hasta detectar la wake word y luego graba la pregunta."""

    def __init__(
        self,
        wake_word: str = "sistema",
        vosk_model_path: str | Path = "models/vosk-model-small-es-0.42",
        sample_rate: int | None = None,
        channels: int = 1,
        chunk_seconds: float = 0.25,
        silence_threshold: int = 550,
        max_silence_seconds: float = 1.2,
        max_record_seconds: float = 15.0,
        speech_start_timeout: float = 4.0,
        pre_speech_seconds: float = 0.35,
        input_device: int | None = None,
    ) -> None:
        self.wake_word = wake_word.lower().strip()
        self.vosk_model_path = Path(vosk_model_path)
        self.channels = channels
        self.chunk_seconds = chunk_seconds
        self.silence_threshold = silence_threshold
        self.max_silence_seconds = max_silence_seconds
        self.max_record_seconds = max_record_seconds
        self.speech_start_timeout = speech_start_timeout
        self.pre_speech_seconds = pre_speech_seconds
        self.input_device = input_device
        self._audio_queue: queue.Queue[bytes] = queue.Queue()

        if not self.vosk_model_path.exists():
            raise AudioListenerError(
                f"No se encontro el modelo Vosk en: {self.vosk_model_path}"
            )

        self.sample_rate = sample_rate or self._detect_sample_rate()
        self.block_size = max(1, int(self.sample_rate * self.chunk_seconds))
        self._wake_word_regex = re.compile(rf"\b{re.escape(self.wake_word)}\b", re.IGNORECASE)
        self._vosk_model = Model(str(self.vosk_model_path))

    def listen_for_command(
        self,
        output_path: str | Path = "temp_audio.wav",
        on_wake_word_detected: Callable[[], None] | None = None,
    ) -> Path:
        """Bloquea hasta detectar la wake word, luego graba hasta silencio."""
        output_path = Path(output_path)
        self._drain_audio_queue()
        wake_recognizer = KaldiRecognizer(self._vosk_model, self.sample_rate)

        stream_kwargs = {
            "samplerate": self.sample_rate,
            "blocksize": self.block_size,
            "dtype": "int16",
            "channels": self.channels,
            "callback": self._audio_callback,
        }
        if self.input_device is not None:
            stream_kwargs["device"] = self.input_device

        try:
            with sd.RawInputStream(**stream_kwargs):
                while True:
                    audio_chunk = self._audio_queue.get()
                    if self._wake_word_detected(wake_recognizer, audio_chunk):
                        if on_wake_word_detected is not None:
                            on_wake_word_detected()

                        recorded_frames = self._record_until_silence()
                        self._save_wav(output_path, recorded_frames)
                        return output_path
        except Exception as exc:
            if isinstance(exc, AudioListenerError):
                raise
            raise AudioListenerError(f"Error al escuchar el microfono: {exc}") from exc

    def _detect_sample_rate(self) -> int:
        try:
            device_info = sd.query_devices(self.input_device, "input")
            return int(device_info["default_samplerate"])
        except Exception as exc:
            raise AudioListenerError(
                "No fue posible consultar el dispositivo de entrada de audio."
            ) from exc

    def _audio_callback(self, indata, frames, time_info, status) -> None:  # noqa: ANN001
        if status:
            # Si hay overflow, seguimos; el siguiente chunk suele recuperarse bien.
            pass
        self._audio_queue.put(bytes(indata))

    def _wake_word_detected(self, recognizer: KaldiRecognizer, audio_chunk: bytes) -> bool:
        if recognizer.AcceptWaveform(audio_chunk):
            result_text = json.loads(recognizer.Result()).get("text", "")
        else:
            result_text = json.loads(recognizer.PartialResult()).get("partial", "")

        return self._contains_wake_word(result_text)

    def _contains_wake_word(self, text: str) -> bool:
        return bool(self._wake_word_regex.search(text.lower()))

    def _record_until_silence(self) -> list[bytes]:
        recorded_frames: list[bytes] = []
        pre_speech_buffer = deque(
            maxlen=max(1, int(self.pre_speech_seconds / self.chunk_seconds))
        )
        speech_started = False
        silent_chunks = 0
        max_silent_chunks = max(1, int(self.max_silence_seconds / self.chunk_seconds))
        wake_deadline = time.monotonic() + self.speech_start_timeout
        record_deadline = time.monotonic() + self.max_record_seconds

        while time.monotonic() < record_deadline:
            try:
                audio_chunk = self._audio_queue.get(timeout=self.chunk_seconds * 2)
            except queue.Empty as exc:
                raise AudioListenerError(
                    "No llego audio desde el microfono durante la grabacion."
                ) from exc

            rms = audioop.rms(audio_chunk, 2)
            has_speech = rms >= self.silence_threshold

            if not speech_started:
                pre_speech_buffer.append(audio_chunk)
                if has_speech:
                    speech_started = True
                    recorded_frames.extend(pre_speech_buffer)
                    silent_chunks = 0
                elif time.monotonic() >= wake_deadline:
                    raise AudioListenerError(
                        "Se detecto la wake word, pero no llego una pregunta valida."
                    )
                continue

            recorded_frames.append(audio_chunk)
            if has_speech:
                silent_chunks = 0
            else:
                silent_chunks += 1
                if silent_chunks >= max_silent_chunks:
                    break

        if not recorded_frames:
            raise AudioListenerError("No fue posible grabar la pregunta del usuario.")

        return recorded_frames

    def _save_wav(self, output_path: Path, frames: list[bytes]) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(b"".join(frames))

    def _drain_audio_queue(self) -> None:
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break
