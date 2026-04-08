# Valkyrie 🛡️

Valkyrie es un asistente de videojuegos impulsado por Inteligencia Artificial Multimodal diseñado para funcionar 100% en local. Escucha tus preguntas a través de un micrófono, "observa" lo que está sucediendo en la pantalla de tu juego y te responde con voz usando modelos de lenguaje visuales de última generación.

El objetivo principal es mantener la inmersión total: obtener consejos, resolver puzzles o revisar estadísticas sin hacer *Alt+Tab* ni buscar en el teléfono.

## 🚀 Características
* **Wake-Word Local:** Escucha pasiva de bajo consumo de recursos usando Vosk.
* **Visión en Tiempo Real:** Captura de pantalla ultrarrápida usando `mss` sin afectar los FPS del juego.
* **Cerebro Multimodal Privado:** Integración con Ollama para procesar inferencias de visión y texto en tu propio hardware (optimizado para tarjetas gráficas modernas).
* **Respuestas Auditivas:** Síntesis de voz natural usando `edge-tts`.

## 🛠️ Requisitos del Sistema
* Tarjeta gráfica compatible con CUDA (Recomendado 8GB+ VRAM).
* Python 3.10 o superior.
* [Ollama](https://ollama.com/) instalado y corriendo de fondo.
* [FFmpeg](https://ffmpeg.org/) instalado y configurado en las variables de entorno (`PATH`).

## ⚙️ Instalación

1. **Clona este repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/Valkyrie.git](https://github.com/tu-usuario/Valkyrie.git)
   cd Valkyrie
   ```

2. **Instala las dependencias de Python:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Descarga el modelo acústico (Vosk):**
   Descarga el modelo [vosk-model-small-es-0.42](https://alphacephei.com/vosk/models) y extráelo dentro de la carpeta `models/` en la raíz del proyecto.

4. **Prepara tu modelo de visión en Ollama:**
   Descarga el modelo multimodal de tu preferencia. Por defecto, Valkyrie utiliza `llama3.2-vision`.
   ```bash
   ollama run llama3.2-vision
   ```

## 🎮 Uso
Asegúrate de que Ollama esté en ejecución y lanza el script principal:

```bash
python main.py
```

Di la palabra de activación (por defecto: **"sistema"**), formula tu pregunta (ej. *"¿Qué debilidad tiene este enemigo en pantalla?"*) y espera la respuesta por tus audífonos.


