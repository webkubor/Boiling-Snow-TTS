# Boiling-Snow-TTS 技术路径与规范 (Technical Path & Standards)

本项目已形成一套成熟的“武侠级”配音自动化生成标准，后续维护与 AI 执行需严格遵循此路径。

## 🏗️ 架构蓝图 (System Architecture)

- **入口指令**：`main.py`（指挥官模式）。
  - `python main.py` ➡️ 加载 `movie_config.json`（微电影模式）。
  - `python main.py podcast` ➡️ 加载 `podcast_config.json`（播客模式）。
- **逻辑分层**：
  - `core/engine.py`：负责 Apple Silicon (MPS/SDPA) 硬件加速与模型加载。
  - `core/cloner.py`：克隆分支，内置 AI 自动裁剪、格式归一化、智能缓存。
  - `core/designer.py`：捏人分支，纯文字指令驱动角色音色创造。
  - `core/utils.py`：负责后期调音（静音留白、去噪、归一化）及元数据记录。

## 📁 资产流转铁律 (Data Flow)

1. **资产库 (`assets/reference_audio/`)**：【永存层】存放原始素材（.m4a, .mp3, .wav）。
2. **智能缓存 (`assets/temp/`)**：【中间层】
   - AI 自动将资产库素材裁剪为 **10s 黄金片段**。
   - 统一转码为 **无损 WAV**（如：`当前参考_角色名.wav`）。
   - **缓存逻辑**：若 temp 中已存在对应标准样音，则**跳过**剪辑与转码，实现秒级启动。
3. **成品库**：【输出层】
   - 微电影成品 ➡️ `assets/output_audio/`
   - 播客成品 ➡️ `assets/podcast_output/`
   - **后期规范**：所有成品强制包含 **1.5s 绝对静音开场**，并执行首尾去噪处理。

## 🎭 身份与品牌 (Identity & Branding)

- **小红书平台**：身份锁定为 **司南烛**。
- **网易云播客《江湖拾音录》**：身份锁定为 **月栖洲**。
- **配音调性**：
  - 电影：深沉、肃杀、带有武侠呼吸感。
  - 播客：温润、知性、贴耳，具备专业播音腔。

---
*记录时间：2026-02-27 | 由小烛为您守护。*
