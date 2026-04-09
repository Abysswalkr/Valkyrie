<div align="center">
  
# Valkyrie 🛡️ 🎮
*Tu copiloto interactivo de videojuegos impulsado por IA Multimodal 100% local.*

[![Español](https://img.shields.io/badge/Idioma-Espa%C3%B1ol-brightgreen?style=for-the-badge)](#) 
[![English](https://img.shields.io/badge/Language-English-blue?style=for-the-badge)](./README.en.md)

</div>

<br/>

**Valkyrie** es un asistente de videojuegos interactivo impulsado por Inteligencia Artificial local. Mediante comandos de voz, captura el estado de tu partida en tiempo real, analiza la pantalla utilizando modelos visuales con Ollama y te proporciona consejos o estrategias narradas auditivamente sin interrumpir tu experiencia de juego.

El objetivo principal es mantener la inmersión total: obtener consejos, resolver puzzles o revisar estadísticas sin hacer *Alt+Tab* ni buscar en el teléfono.

## ✨ Características Principales

* 🎙️ **Wake-Word Local:** Escucha pasiva de bajo consumo usando Vosk y transcripción ultra veloz con *faster-whisper*.
* 👁️ **Visión en Tiempo Real:** Captura de pantalla inmediata usando `mss` que no interfiere con los FPS de tu juego.
* 🧠 **Cerebro Multimodal Privado:** Procesamiento 100% en tu máquina usando Ollama (optimizado para tarjetas gráficas y CPUs modernas).
* 🔊 **Respuestas Auditivas Naturales:** Síntesis de voz fluida gracias a la inyección de la API de Microsoft (`edge-tts`).

## 🛠️ Requisitos del Sistema

* Tarjeta gráfica dedicada recomendada (min. 4GB VRAM para el modelo de visión ligero).
* [Python 3.10](https://www.python.org/) o superior.
* [Ollama](https://ollama.com/) instalado y corriendo en segundo plano.

## 🚀 Instalación y Configuración

**1. Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/Valkyrie.git
cd Valkyrie
```

**2. Descargar las dependencias:**
```bash
pip install -r requirements.txt
```

**3. Modelos de Audio (Vosk):**
* Descarga el pequeño modelo de bolsillo de español: [vosk-model-small-es-0.42](https://alphacephei.com/vosk/models) 
* Extrae su carpeta y asegúrate de que quede el contenido directamente en la ruta: `models/vosk-model-small-es-0.42/`

**4. Instalar el cerebro visual local (Ollama):**
Por defecto, Valkyrie utiliza el veloz modelo híbrido `llava-phi3` para maximizar tus FPS.
```bash
ollama pull llava-phi3
```

## 🎮 Guía de Uso

Ya con todo listo, lanza tu script principal y entra a algún videojuego:

```bash
python main.py
```

Di en voz alta la palabra de activación (por defecto **"sistema"** o la que dictes), luego inmediatamente has tu consulta (ejemplo: *"Sistema, ¿Qué debilidad tiene este enemigo en pantalla?"*)... y prepárate para escuchar los consejos que estabas buscando.

