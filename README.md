# 🏔️ Boiling-Snow-TTS
> **工业级武侠语音合成引擎 | 专为 Apple Silicon 深度优化 | 基于 Qwen3-TTS**

<p align="center">
  <img src="assets/cover.jpg" width="100%" alt="Boiling-Snow-TTS Cover"/>
</p>

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](pyproject.toml)
[![Platform](https://img.shields.io/badge/Platform-macOS%20(M1/M2/M3)-black.svg)](#-硬件加速优化-hardware-acceleration)

**Boiling-Snow-TTS** 是一个面向专业创作的 AI 配音解决方案。它不仅继承了阿里巴巴 Qwen3-TTS 的核心生成能力，更针对影视创作流程进行了深度重构，旨在为《沸腾之雪》等高品质武侠内容提供具备“灵魂”的中文配音。

---

## 🚀 核心卖点：为什么选择本项目？

### 1. Apple Silicon 原生性能巅峰
原版 TTS 项目通常强依赖 NVIDIA 的 CUDA 环境。本项目通过底层改造，实现了对 **Apple M 芯片** 的原生支持。利用 **MPS (Metal Performance Shaders)** 与 **SDPA (Scaled Dot Product Attention)**，在 MacBook M3 Pro 等设备上实现了秒级的成品产出，彻底告别“Mac 跑大模型像幻灯片”的历史。

### 2. 导演级“剧本即生成”流转
首创 **JSON 驱动架构**。创作者无需接触 Python 代码，通过修改 `configs/config.json` 即可统筹管理：
- **情感表达**：通过指令控制声音的沧桑、杀机、柔情。
- **角色路由**：一键切换克隆模式、捏人模式或预设模式。
- **自动化交付**：生成的音频自带规范化的中文命名，直接拖入 FCPX 或 PR 即可剪辑。

### 3. AI 资产原子化自理
内置 **AI 自动音频预处理** 模块。当您投入一段长参考音频时，引擎会自动检测音质并裁剪出最佳的 **8-10 秒克隆黄金片段**，消除了繁琐的手工剪辑环节。

---

## ⚔️ 核心功能模块 (Core Modules)

| 模式 | 技术原理 | 适用场景 |
| :--- | :--- | :--- |
| **声音克隆 (Base)** | 零样本 (Zero-shot) 音色复刻 | 100% 还原特定演员/说书人的音色 |
| **音色设计 (VoiceDesign)** | 自然语言指令驱动生成 | 凭空创造全新的武侠角色（如：苍老、邪魅） |
| **官方精品 (CustomVoice)** | 预设高质量算子调用 | 快速为配角、路人提供稳定的音质输出 |

---

## 🤖 模型架构矩阵 (Model Gallery)

项目内置了 4 套针对不同创作阶段优化的配音算子：

- **1.7B 系列 (全量级 - 推荐)**：成品级引擎。对“武侠语境”理解极深，支持精细的 `emotion` 与 `tone` 控制。
- **0.6B 系列 (轻量级)**：预览级引擎。极速出样，内存占用低至 2GB，适合前期对台词节奏。

---

## 🛠️ 快速开始 (Quick Start)

### 1. 一键部署
针对 Mac 用户提供全自动安装脚本，一行命令搞定环境、依赖与模型下载：
```bash
chmod +x install.sh && ./install.sh
```

### 2. 文案配置
编辑 `configs/config.json`：
```json
{
  "model_type": "Base",
  "persona": "narrator",
  "text": "雪落江湖，热血难凉。这一笔风月，你可敢接？",
  "emotion": "深沉、肃杀、带有浓厚的江湖感",
  "episode": "01",
  "title": "江湖序章"
}
```

### 3. 启动引擎
```bash
source .venv/bin/activate
python main.py
```

---

## 🗺️ 路线图 (Roadmap)
- [x] Apple Silicon (M-Series) 硬件加速优化
- [x] AI 自动参考音频裁剪逻辑
- [x] 多模式智能路由引擎
- [ ] 批量剧本文案自动生成排队系统
- [ ] Web 端可视化配置界面 (Gradio 深度集成)

---

## 📜 开源协议与鸣谢
本项目基于阿里巴巴 **Qwen3-TTS** 二次开发，遵循 [Apache-2.0 License](LICENSE)。
特别鸣谢 Qwen 团队提供的强大底层模型支持。

---
*一笔写风月，一心藏滚烫。*
