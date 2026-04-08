from __future__ import annotations

from pathlib import Path

import mss
from PIL import Image


class VisionCaptureError(RuntimeError):
    """Errores relacionados con la captura de pantalla."""


class VisionCapture:
    """Captura el monitor principal y lo guarda como JPG temporal."""

    def __init__(self, monitor_index: int = 1, jpg_quality: int = 90) -> None:
        self.monitor_index = monitor_index
        self.jpg_quality = jpg_quality

    def capture(self, output_path: str | Path = "temp_capture.jpg") -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with mss.mss() as sct:
                if len(sct.monitors) <= self.monitor_index:
                    raise VisionCaptureError(
                        f"No existe el monitor {self.monitor_index} en esta maquina."
                    )

                monitor = sct.monitors[self.monitor_index]
                screenshot = sct.grab(monitor)
                image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                image.save(
                    output_path,
                    format="JPEG",
                    quality=self.jpg_quality,
                    optimize=True,
                )
        except Exception as exc:
            if isinstance(exc, VisionCaptureError):
                raise
            raise VisionCaptureError(
                f"Error al capturar la pantalla principal: {exc}"
            ) from exc

        return output_path
