# Boiling-Snow-TTS (Wuxia Voice Generation Engine)

[中文文档](README.md) | English

This project is a custom-tailored **AI Voice Generation Engine** designed for high-quality Wuxia (Chinese martial arts) content. Powered by Alibaba's Qwen3-TTS, it has been heavily refactored to provide a professional, automated pipeline for cinematic voiceover production on Apple Silicon.

---

## 🎯 Key Features & Enhancements

This project significantly evolves the original Qwen3-TTS repository into a production-ready toolkit:

1. **JSON-Driven Architecture**: Total decoupling of creative content from code. Manage episodes, characters, and emotions via runtime JSON configs.
2. **Apple Silicon Native Acceleration**: Fully optimized for **M1/M2/M3** chips. Implements `MPS` hardware acceleration and `SDPA` (Scaled Dot Product Attention), bypassing the NVIDIA CUDA requirement.
3. **Unified Quaternary Engine**: Seamlessly handles "Voice Cloning", "Voice Design", "Dialogue Theatre", and "Podcast Column" modes within a single command (`main.py`).
4. **AI Auto-Processing (Ref-Opt)**: Built-in intelligent audio preprocessing. Automatically applies a **1.5s safety offset**, strips background noise, and normalizes clips to lossless WAV format.
5. **Smart Caching**: Implements a timestamp-based caching system in `assets/temp/`, enabling instant repeated generation by skipping redundant audio processing.

---

## ⚔️ Core Modules

The engine isolates four major functionalities to ensure modularity and creative control:

### 1. Voice Cloning (`Base` Mode)
- **Logic**: Replicates specific voices from reference samples.
- **Workflow**: Drop a raw audio file into `assets/reference_audio/` named as `{Character}_参考.wav`. The AI handles the rest.

### 2. Voice Design (`VoiceDesign` Mode)
- **Logic**: Generates unique voices from scratch using text prompts (e.g., "A deep, raspy voice of a 50-year-old master").
- **Workflow**: Ideal for casting new characters without human references.

### 3. Dialogue Theatre (`Dialogue`)
- **Logic**: Supports multi-character scripts with automatic scene stitching.
- **Workflow**: Define a list of `lines` in the config; the AI manages character switches and inserts natural breathing pauses.

### 4. Podcast Column (`Podcast`)
- **Logic**: Specialized mode for the *"Jianghu Sound Picker"* series.
- **Workflow**: Locked identity (Yue Qizhou) with professional radio-style post-tuning.

---

## 🤖 Models Gallery

- **1.7B Tier (Full - Recommended)**: Professional-grade engines. Supports fine-grained `emotion` and `tone` instructions.
- **0.6B Tier (Lite)**: Rapid prototyping engines. Low memory footprint (~2GB) and ultra-fast generation.

---

## 📥 Model Downloads

Download weights and place them in the `models/` directory:

| Model | Directory | Use Case |
| :--- | :--- | :--- |
| **Qwen3-TTS-1.7B-Base** | `models/Base-1.7B` | High-quality cloning |
| **Qwen3-TTS-1.7B-VoiceDesign** | `models/VoiceDesign-1.7B` | Voice creation |

---

## 🚀 Quick Start

### 1. One-Click Setup
```bash
chmod +x install.sh && ./install.sh
```

### 2. Run the Engine
```bash
source .venv/bin/activate
# For Micro-movies
python main.py
# For Podcast series
```

---
*License: Apache-2.0*
