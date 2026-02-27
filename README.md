# Boiling-Snow-TTS (沸腾之雪·武侠配音引擎)

本项目是专为《沸腾之雪》剧集设计的 AI 配音生成工具。通过克隆指定角色的音色（如【说书人】），生成具有武侠质感的中文对白。

## 🤖 AI 代理执行协议 (AI execution Protocol)

### 1. 核心逻辑 (Core Logic)
- **输入控制**：读取 `configs/config.json`。
- **音色参考**：读取 `assets/reference_audio/{persona}_ref.mp3`。
- **执行入口**：运行 `python boiling_snow_clone.py`。
- **输出目标**：生成的音频存放在 `assets/output_audio/`。

### 2. 模型切换 (Model Switching)
支持在 `config.json` 中通过 `model_size` 字段切换模型：
- **"0.6B"**：轻量化模型，生成速度极快，适合快速出样。
- **"1.7B"**：全量模型（推荐），支持通过 `emotion` 和 `tone` 字段进行指令级情绪控制。

### 3. 环境与路径 (Environment & Paths)
- **根目录**：`/Users/webkubor/Desktop/create/Qwen3-TTS/`
- **虚拟环境**：使用 `./.venv/bin/python` 执行。
- **模型路径**：`models/Base-{model_size}/`

## 📁 自动化目录规范

- `assets/reference_audio/`：存放角色音色底稿（建议 8-10s）。
- `assets/output_audio/`：存放生成结果。
- `configs/config.json`：**唯一操作入口**，修改文案与模型参数。

---
*雪落江湖，热血难凉。*
