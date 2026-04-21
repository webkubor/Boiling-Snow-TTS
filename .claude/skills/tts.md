---
name: tts
project: snowvoice-studio
for: ai-agent
---

# SnowVoice Studio — Agent 调用 SOP

## 前置

```bash
cd ~/Desktop/personal/tts
source .venv/bin/activate
# 或直接用绝对路径：.venv/bin/snowvoice
```

## 核心命令

```bash
# 查看可用音色
snowvoice voice list

# 声音克隆（角色 + 台词 → wav）
snowvoice clone <persona> "<台词>" [-o output.wav]

# 音色设计（文字描述 → 新音色）
snowvoice design <name> "<建模短句>" --tone "<风格描述>"

# 多角色对话（脚本文件 → 多段音频）
snowvoice dialogue --script <script.txt>
```

## 输出

- 默认输出到 `out/`
- 文件名格式：`<persona>_YYYYMMDD_HHMMSS.wav`

## 红线

- 调用前必须 `source .venv/bin/activate`，否则 `snowvoice` 找不到
- `--tone` 参数用中文描述效果更准确
- 首次运行需确认 `models/` 目录有模型文件
