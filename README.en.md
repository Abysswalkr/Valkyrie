<div align="center">
  
# Valkyrie 🛡️ 🎮
*Your interactive multimodal AI gaming co-pilot, running 100% locally.*

[![Español](https://img.shields.io/badge/Idioma-Espa%C3%B1ol-brightgreen?style=for-the-badge)](./README.md) 
[![English](https://img.shields.io/badge/Language-English-blue?style=for-the-badge)](#)

</div>

<br/>

**Valkyrie** is an interactive AI gaming assistant powered by local vision and language models. Using voice commands, it captures your live gameplay, analyzes the screen context via Ollama, and audibly speaks out real-time strategies and tips, acting as a seamless co-pilot without interrupting your actual gaming experience.

The main goal is to maintain total immersion: get tips, solve puzzles, or check stats without doing *Alt+Tab* or searching on your phone.

## ✨ Key Features

* 🎙️ **Local Wake-Word:** Low-resource passive listening using Vosk, and ultra-fast transcription with *faster-whisper*.
* 👁️ **Real-Time Vision:** Instant screen capturing using `mss` that won't interfere with your game's FPS.
* 🧠 **Private Multimodal Brain:** 100% on-device processing via Ollama (optimized for modern GPUs and CPUs).
* 🔊 **Natural Audio Responses:** Fluid voice synthesis injected by Microsoft API (`edge-tts`).

## 🛠️ System Requirements

* Dedicated graphics card recommended (min. 4GB VRAM for lightweight vision models).
* [Python 3.10](https://www.python.org/) or higher.
* [Ollama](https://ollama.com/) installed and running in the background.

## 🚀 Installation & Setup

**1. Clone the repository:**
```bash
git clone https://github.com/your-username/Valkyrie.git
cd Valkyrie
```

**2. Download dependencies:**
```bash
pip install -r requirements.txt
```

**3. Audio Models (Vosk):**
* Download the small pocket acoustic model: [vosk-model-small-es-0.42](https://alphacephei.com/vosk/models) 
* Extract its folder and make sure its contents are placed directly inside: `models/vosk-model-small-es-0.42/`

**4. Install the local vision brain (Ollama):**
By default, Valkyrie uses the fast hybrid model `llava-phi3` to maximize your FPS.
```bash
ollama pull llava-phi3
```

## 🎮 Usage Guide

Once everything is ready, launch your main script and jump into any video game:

```bash
python main.py
```

Say the wake-word explicitly out loud (default: **"sistema"** or whatever you speak), then immediately ask your question (example: *"System, what weakness does this enemy on screen have?"*)... and get ready to listen to the advice you were looking for.
