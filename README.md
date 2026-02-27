# Boiling-Snow-TTS (沸腾之雪·武侠配音项目)

本项目是基于 Qwen3-TTS 开发的专用武侠配音生成工具，专为《沸腾之雪》剧集及相关武侠内容提供高质量、极具江湖感的中文配音生成。

## 🌟 项目特色

- **武侠风骨**：针对武侠语境优化的中文克隆与生成。
- **角色音色管理**：内置【说书人/旁白】等核心音色，支持快速调用。
- **极简操作**：通过 `boiling_snow_clone.py` 一键生成指定角色的旁白。
- **自动化剪辑**：自动处理 8-10s 的最佳参考音频片段（逻辑持续优化中）。

## 📁 目录结构

- `assets/reference_audio/`：**参考音频目录**。存放各角色的原始音色片段（如 `narrator_ref.mp3`）。
- `assets/output_audio/`：**生成目录**。所有生成的配音成品都会自动存放在此处。
- `models/`：模型权重存放目录（已在 .gitignore 中忽略）。
- `boiling_snow_clone.py`：**核心生成脚本**。

## 🚀 快速开始

### 1. 环境准备
确保已安装必要的依赖（建议使用 `uv` 或 `pip`）：
```bash
pip install torch soundfile qwen-tts
```

### 2. 生成配音
直接运行核心脚本即可生成当前的旁白：
```bash
python boiling_snow_clone.py
```

## 🎙️ 角色调用指南

- **生成旁白/说书人**：默认调用 `assets/reference_audio/narrator_ref.mp3`。
- **添加新角色**：
  1. 将 8-10s 的纯净人声音频放入 `assets/reference_audio/`。
  2. 在脚本中修改 `ref_audio` 路径即可。

## 📜 开源协议
本项目基于 Qwen3-TTS 修改，遵循原项目的开源协议。

---
*雪落江湖，热血难凉。一笔写风月，一心藏滚烫。*
