# 🏔️ Boiling-Snow-TTS
> **工业级武侠语音合成引擎 | 专为 Apple Silicon 深度优化 | 基于 Qwen3-TTS**

<p align="center">
  <img src="assets/cover.jpg" width="100%" alt="Boiling-Snow-TTS Cover"/>
</p>

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](pyproject.toml)
[![Platform](https://img.shields.io/badge/Platform-macOS%20(M1/M2/M3)-black.svg)](#-硬件加速优化-hardware-acceleration)

**Boiling-Snow-TTS** 是一个面向专业创作的 AI 配音解决方案。它继承了 Qwen3-TTS 的强大能力，并通过深度重构，为《沸腾之雪》等高品质武侠内容提供具备“导演级”控制力的中文配音。

---

## 🐣 小白 3 分钟快速上手 (3-Min Quick Start)

本项目的核心理念是：**让不懂代码的创作者也能轻松驾驭顶级 TTS。**

### 第一步：一键“激活”工坊
打开终端，粘贴运行以下命令（自动装环境、下模型）：
```bash
chmod +x install.sh && ./install.sh
```

### 第二步：像写剧本一样改配置
找到项目里的 `configs/config.json`，把你想说的话填进去。

**💡 声音克隆技巧 (Voice Cloning)：**
如果你想复刻某个声音，只需将该角色的 **任意长度原始录音** 放入目录：`assets/reference_audio/`，并命名为 `{角色名}_ref.mp3`。
**无需手动剪辑**，项目内置的 AI 模块会自动为您截取最佳的 10 秒片段进行克隆。
然后在 `config.json` 中把 `persona` 设置为该 `角色名`，并将 `model_type` 设为 `Base` 即可。

### 第三步：一键收片
在终端运行：
```bash
source .venv/bin/activate
python main.py
```
**恭喜！** 你的配音成品已经躺在 `assets/output_audio/` 目录里🎉。

---

## 🛠️ 基于原项目的深度改造 (Key Enhancements)

本项目在阿里巴巴开源项目 **Qwen3-TTS** 的基础上，进行了面向工业级创作的深度重构：

1. **JSON 驱动架构**：彻底解耦文案与逻辑。通过 `configs/config.json` 统筹管理，实现“填空式”生成体验。
2. **Mac M 芯片原生加速**：引入 `MPS` 硬件加速和 `SDPA` 注意力机制，解决了 NVIDIA `flash-attn` 的限制，使 Mac 生成速度提升数倍。
3. **三位一体引擎整合**：将“声音克隆”、“音色设计”及“官方预设”整合进单一路由，支持根据配置自动派发。
4. **AI 自动音频裁剪**：新增自动化预处理模块。系统会自动将参考音频截取为 8-10 秒的黄金时长，无需人工剪辑。
5. **规范化资产管理**：建立了标准化的 `assets` 体系，生成带中文标题的成品库，方便直接对接剪辑软件。
6. **AI Agent 执行协议**：为 AI 助手（如小烛）设计了明确的 SOP 协议，使其具备自主根据剧本创作的能力。

---

## ⚔️ 核心功能模块 (Core Modules)

| 模式 | 技术原理 | 操作流程 |
| :--- | :--- | :--- |
| **声音克隆 (Base)** | 零样本 (Zero-shot) 复刻 | 放入 `{角色名}_ref.mp3` 到参考目录，AI 自动学习 |
| **音色设计 (VoiceDesign)** | 指令驱动捏人 | 填写 `emotion` & `tone` 描述，AI 凭空创造声音 |
| **官方精品 (CustomVoice)** | 预设高质量算子 | 在配置中指定 `speaker` 名字，快速出片 |

---

## 🚀 硬件加速优化 (Hardware Acceleration)

本项目核心脚本 `main.py` 已针对 **Apple Silicon (M1/M2/M3)** 芯片进行深度优化：
- **MPS 加速**：利用 Mac GPU 进行矩阵运算。
- **SDPA**：强制启用原生注意力机制加速，绕过 NVIDIA 环境限制。
- **bfloat16 精度**：大幅降低内存占用的同时，保持 1.7B 大模型的高音质输出。

---

## 🤖 模型架构矩阵 (Model Gallery)

- **Base-1.7B (全量级 - 推荐)**：成品级引擎。支持精细的情绪控制。
- **Base-0.6B (轻量级)**：预览级引擎。极速出样，内存占用低（~2GB）。
- **VoiceDesign-1.7B**：创意引擎。用于文字描述造人。
- **CustomVoice-1.7B**：精品库。包含 9 种官方调优音色。

---

## 📥 模型下载 (Model Downloads)

请下载模型并放置在 `models/` 目录下：

| 模型名称 | 对应目录 | 下载命令 (ModelScope) |
| :--- | :--- | :--- |
| **Base-1.7B** | `models/Base-1.7B` | `modelscope download --model Qwen/Qwen3-TTS-12Hz-1.7B-Base --local_dir ./models/Base-1.7B` |
| **VoiceDesign-1.7B** | `models/VoiceDesign-1.7B` | `modelscope download --model Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign --local_dir ./models/VoiceDesign-1.7B` |

---

## 🗺️ 路线图 (Roadmap)
- [x] Apple Silicon 硬件加速
- [x] AI 自动参考音频裁剪
- [x] 多模式智能路由
- [ ] 批量剧本排队系统
- [ ] Web 可视化配置界面

---

## 📜 开源协议
本项目基于阿里巴巴 **Qwen3-TTS** 二次开发，遵循 [Apache-2.0 License](LICENSE)。

---
*雪落江湖，热血难凉。*
