# AI Context

> **🤖 AI Agents 导航**: 本项目遵循 Standard Workflow。
> 请优先阅读 [.agent/PROJECT.md](.agent/PROJECT.md) 获取上下文与任务索引。

# 🏔️ Boiling-Snow-TTS
> **工业级中文语音合成引擎 | 专为 Apple Silicon 深度优化 | 基于 Qwen3-TTS**

<p align="center">
  <img src="assets/cover.jpg" width="100%" alt="Boiling-Snow-TTS Cover"/>
</p>

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](pyproject.toml)
[![Platform](https://img.shields.io/badge/Platform-macOS%20(M1/M2/M3)-black.svg)](#-硬件加速优化-hardware-acceleration)

**Boiling-Snow-TTS** 是一个面向专业创作的 AI 配音解决方案。它继承了 Qwen3-TTS 的强大能力，并通过深度重构，为高品质中文内容提供具备“导演级”控制力的语音合成能力。

---

## 🐣 小白 3 分钟快速上手 (3-Min Quick Start)

本项目的核心理念是：**让不懂代码的创作者也能轻松驾驭顶级 TTS。**

### 第一步：一键“激活”工坊
打开终端，粘贴运行以下命令（自动装环境、下模型）：
```bash
chmod +x install.sh && ./install.sh
```

📚 **命令总表**：见 [docs/COMMANDS.md](docs/COMMANDS.md)

### AI 初始化门禁 (必开)
```bash
# 校验 .agent 必备结构与 README 头部导航
npm run ai:check

# 一次性安装 pre-commit 门禁（推荐）
npm run hooks:install
```

### 第二步：像写剧本一样改配置
项目运行态只保留 4 个核心 JSON：
- **克隆脚本配置**：`configs/clone.json`
- **设计脚本配置**：`configs/design.json`
- **对话拼接配置**：`configs/dialogue.json`
- **声音映射配置**：`configs/personas.json`
- **角色映射**：编辑 `configs/personas.json`（自定义中英文角色名映射，此文件不上传）。

### 第三步：一键收片
在终端运行：
```bash
source .venv/bin/activate
# 默认生成微电影配音
python main.py
# 指定克隆 / 设计 / 对话
python main.py clone
python main.py design
python main.py dialogue
```
**恭喜！** 你的配音成品已经躺在 `assets/output_audio/` 目录里🎉。

**💡 声音克隆技巧 (Voice Cloning)：**
- 0-1 新角色克隆：可直接在配置中提供 `reference_audio`，系统会自动降噪并裁剪黄金 8-10s 到 `assets/temp/`。
- 生产阶段生成：建议将角色注册到 `personas.json`，并统一基于 `assets/temp/` 的标准样音调度。

---

## 🛠️ 基于原项目的深度改造 (Key Enhancements)

本项目在阿里巴巴开源项目 **Qwen3-TTS** 的基础上，进行了面向工业级创作的深度重构：

1. **JSON 驱动架构**：彻底解耦文案与逻辑。通过 `clone/design/dialogue + personas` 管理配置，实现长期模板稳定。
2. **Mac M 芯片原生加速**：引入 `MPS` 硬件加速和 `SDPA` 注意力机制，解决了 NVIDIA `flash-attn` 的限制，使 Mac 生成速度提升数倍。
3. **三位一体引擎整合**：将“声音克隆”、“音色设计”、“对话剧场”整合进单一路由，支持根据配置自动派发。
4. **AI 自动音频处理**：内置 Ref-Opt 原子化组件。自动对参考音频进行 1.5s 安全避障裁剪、物理脱水去噪及无损 WAV 格式归一化。
5. **规范化资产管理**：建立了标准化的 `assets` 体系，生成带中文标题的成品库，方便直接对接剪辑软件。
6. **AI Agent 执行协议**：为 AI 助手（如小烛）设计了明确的 SOP 协议，使其具备自主根据剧本创作的能力。

---

## ⚔️ 核心功能模块 (Core Modules)

| 模式 | 技术原理 | 操作/触发方式 |
| :--- | :--- | :--- |
| **声音克隆 (Base)** | 零样本 (Zero-shot) 复刻 | 放入 `{角色名}_参考.wav/mp3/m4a` 到参考目录 |
| **音色设计 (VoiceDesign)** | 指令驱动捏人 | 在配置中填写 `emotion` & `tone` 描述文案 |
| **对话剧场 (Dialogue)** | 多角色调度与缝合 | 在配置中编写 `lines` 台词列表（支持自动呼吸感插入） |
| **官方精品 (CustomVoice)** | 预设高质量算子 | 在配置中指定官方 `speaker` 名字（如 Vivian） |

---

## 🔁 生产流程约定 (重要)

- **0-1 阶段（克隆 / 设计）**：允许不依赖 `personas.json`。  
  - 克隆可通过 `reference_audio` 直接输入原始参考音频，自动降噪并提取黄金 **8-10s** 到 `assets/temp/`。  
  - 若未设置 `persona`，单人克隆输出文件名默认回退为 `reference_audio` 的文件名（去扩展名）。  
  - 设计默认先输出到 `out/` 供试听；确认满意后，将 `commit_to_temp=true` 再执行一次，即可沉淀到 `assets/temp/` 并自动生成 personas 映射与 `configs/generated/<voice_name>_generate.json`。
  - 设计模式文案采用**长度门禁**：最多 45 字；可留空，系统会自动填充默认短句。设计重点是 `tone`/`emotion` 等音色 prompt。
- **生产阶段（单角色生成 / 对话）**：基于 `assets/temp/` 的标准样音，并通过 `personas.json` 做角色匹配与调度。

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

## 🌐 WebUI 控制台 (FastAPI + React)

新增本地可视化控制台，支持：
- 页面上传参考音频并自动提取黄金样音
- 页面配置克隆/设计/对话参数并触发生成
- 生成后页面内直接试听与下载

启动方式：
```bash
source .venv/bin/activate
pip install -e .
npm --prefix webui install
```

后端 API（终端 1）：
```bash
npm run api:dev
```

前端 WebUI（终端 2）：
```bash
npm run web:dev
```

打开浏览器访问：
`http://127.0.0.1:5173`

### WebUI 相关命令速查
```bash
# 安装前端依赖
npm --prefix webui install

# 启动 API
npm run api:dev

# 启动 WebUI
npm run web:dev

# 构建 WebUI
npm run web:build
```

---

## 📜 开源协议
本项目基于阿里巴巴 **Qwen3-TTS** 二次开发，遵循 [Apache-2.0 License](LICENSE)。

---
