# Boiling-Snow-TTS (沸腾之雪·武侠配音引擎)

本项目是专为《沸腾之雪》剧集设计的 AI 配音生成工具。通过克隆指定角色的音色（如【说书人】），生成具有武侠质感的中文对白。

## 🤖 AI 代理执行协议 (AI execution Protocol)

### 1. 核心逻辑 (Core Logic)
- **输入控制**：读取 `configs/config.json`。
- **音色参考**：读取 `assets/reference_audio/{persona}_ref.mp3`。
- **执行入口**：运行 `python boiling_snow_clone.py`。
- **输出目标**：生成的音频存放在 `assets/output_audio/`。

### 2. 模型库说明 (Models Gallery)
项目中 `models/` 目录下包含以下模型，其用途如下：
- **Base-0.6B**：轻量化基础模型。**用途**：快速声音克隆。优点是速度极快，内存占用低（~2GB），适合快速迭代样音。
- **Base-1.7B**：全量基础模型。**用途**：**高质量声音克隆**。支持 `emotion` 和 `tone` 指令控制，语气更细腻，适合最终成品。
- **CustomVoice-1.7B**：预设音色模型。**用途**：使用官方预设的 9 种精品音色（如 Vivian, Uncle_Fu 等），支持自然语言描述生成（Voice Design）。

### 3. 环境与路径 (Environment & Paths)
- **根目录**：`/Users/webkubor/Desktop/create/Qwen3-TTS/`
- **虚拟环境**：使用 `./.venv/bin/python` 执行。

## 📁 自动化目录规范

- `assets/reference_audio/`：存放角色音色底稿（建议 8-10s）。
- `assets/output_audio/`：存放生成结果。
- `configs/config.json`：**唯一操作入口**，修改文案、情绪及文件名。

---
*雪落江湖，热血难凉。*
