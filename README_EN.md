# Boiling-Snow-TTS (Wuxia Voice Generation Engine)

[中文文档](README.md) | English

This project is a custom-tailored **AI Voice Generation Engine** designed for the Wuxia (Chinese martial arts) micro-movie *"Boiling Snow"*. Built upon Alibaba's open-source Qwen3-TTS technology, it provides an automated, industrial-grade pipeline for generating highly expressive, cinematic Chinese voiceovers.

---

## 🎯 Key Features & Enhancements

This project significantly refactors the original Qwen3-TTS repository to provide a "director-level" out-of-the-box experience:

1. **JSON-Driven Architecture**: Total decoupling of script content from Python logic. Creators only need to edit `configs/config.json` to manage episodes, titles, dialogue, and emotions.
2. **Apple Silicon (M1/M2/M3) Native Acceleration**: Solves the original project's strict dependency on NVIDIA's `flash-attn`. Implements `MPS` hardware acceleration and `SDPA` (Scaled Dot Product Attention), drastically boosting generation speed on Mac devices.
3. **Unified Trinity Engine**: Consolidates "Voice Cloning", "Voice Design", and "Preset Voices" into a single, intelligent routing script (`boiling_snow_clone.py`).
4. **AI Auto-Clipping**: No need to manually trim reference audio. Just drop a raw audio file into the folder, and the AI will automatically extract the optimal 8-10 second segment for cloning.
5. **Standardized Asset Management**: Generates beautifully formatted output files (e.g., `[Clone]Narrator_Ep09_Title.wav`) directly ready for video editing software.

---

## ⚔️ Core Modules

The engine isolates two main functionalities to prevent parameter pollution:

### 1. Voice Cloning (`Base` Mode)
- **How it works**: Provide a raw reference audio file of the target character (e.g., a narrator) in `assets/reference_audio/{persona}_ref.mp3`. The AI auto-clips it and clones the voice.
- **Trigger**: Set `"model_type": "Base"` in `config.json`.
- **Use Case**: 100% voice replication of a specific actor.

### 2. Voice Design (`VoiceDesign` Mode)
- **How it works**: Create a voice out of thin air using only text descriptions (e.g., "A 50-year-old man with a deep, raspy voice").
- **Trigger**: Set `"model_type": "VoiceDesign"` in `config.json`.
- **Use Case**: Instantly casting unique voices for new Wuxia characters without needing a human reference.

---

## 🤖 Models Gallery

The `models/` directory houses different tiers of engines:

- **Base-0.6B**: Lightweight cloning engine. Extremely fast, low memory footprint (~2GB). Ideal for rapid prototyping.
- **Base-1.7B (Recommended)**: Full-scale cloning engine. Supports fine-grained emotion and tone control instructions. Perfect for final cinematic outputs.
- **VoiceDesign-1.7B**: The creative engine used for generating brand new voices from text prompts.
- **CustomVoice-0.6B/1.7B**: Contains 9 official high-quality preset voices.

---

## 📥 Model Downloads

Model weights are not included in this repository. Please download them using the following links or commands:

| Model Name | Local Directory | Use Case |
| :--- | :--- | :--- |
| [Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base) | `models/Base-1.7B` | **Recommended**. High-quality cloning. |
| [Qwen3-TTS-12Hz-1.7B-VoiceDesign](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign) | `models/VoiceDesign-1.7B` | For creating new voices via text prompts. |

### Download via HuggingFace
```bash
pip install -U "huggingface_hub[cli]"
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-Base --local-dir ./models/Base-1.7B
```

---

## 🚀 Quick Start

### 1. One-Click Installation
For Mac/Linux users, simply run the setup script to initialize the environment, install dependencies, and download the core models:

```bash
chmod +x install.sh
./install.sh
```

### 2. Configure Your Script
Edit `configs/config.json`:
```json
{
  "episode": "01",
  "title": "The Legend Begins",
  "persona": "narrator",
  "model_type": "Base",
  "model_size": "1.7B",
  "text": "The martial world is vast, and the snow falls silently.",
  "emotion": "deep, solemn",
  "tone": "low, raspy",
  "language": "Chinese"
}
```

### 3. Generate Audio
Run the unified engine:
```bash
source .venv/bin/activate
python main.py
```
The output will be saved in `assets/output_audio/`.

---
*License: Apache-2.0*
