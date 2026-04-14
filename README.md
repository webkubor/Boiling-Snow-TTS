# SnowVoice Studio

开源中文语音工作台，给人类、AI、agent 都能直接安装和运行。

> 当前阶段：**CLI 可用，WebUI 进入规划阶段。**
>  
> 本项目基于阿里巴巴开源的 **Qwen3-TTS** 二次开发，先把“本地可跑、命令清晰、适合自动化”做好，再补完整 WebUI。

<p align="center">
  <img src="assets/cover.jpg" width="100%" alt="SnowVoice Studio Cover"/>
</p>

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](pyproject.toml)
[![Platform](https://img.shields.io/badge/Platform-macOS%20Apple%20Silicon-black.svg)](pyproject.toml)

[English README](README_EN.md)

## 这个项目现在解决什么问题

- 让非技术用户也能在本地跑通中文 TTS，不需要自己拼环境。
- 让 AI / agent 可以用稳定命令自动安装、自动调用、自动出音频。
- 把“声音克隆、音色设计、对话生成”统一到一个开源工作台里。

## 当前状态

| 能力 | 状态 | 说明 |
| :--- | :--- | :--- |
| CLI | 已可用 | 主入口为 `snowvoice` |
| 声音克隆 | 已可用 | 支持复用 `personas.json` 与标准样音 |
| 音色设计 | 已可用 | 支持文字描述生成新音色 |
| 对话生成 | 已可用 | 当前走 `python main.py dialogue` |
| WebUI | 规划中 | 本次先把命名、定位和路线图理顺 |

## 3 分钟上手

### 1. 克隆仓库

```bash
git clone https://github.com/webkubor/snowvoice-studio.git
cd snowvoice-studio
```

### 2. 一键安装

```bash
chmod +x install.sh
./install.sh
```

安装脚本会自动完成这些事：

- 创建 `.venv`
- 安装 Python 依赖
- 安装项目本体
- 下载基础模型到 `models/`

### 3. 激活并查看命令

```bash
source .venv/bin/activate
snowvoice --help
```

## 给 AI / agent 的最短启动路径

```bash
git clone https://github.com/webkubor/snowvoice-studio.git
cd snowvoice-studio
./install.sh
source .venv/bin/activate
snowvoice --help
```

如果要直接执行现有能力，优先用下面这些入口：

```bash
# 查看音色
snowvoice voice list

# 用已有 persona 克隆一段语音
snowvoice clone <persona> "你好，欢迎使用 SnowVoice Studio"

# 设计新音色
snowvoice design <voice_name> "这是一段建模短句" --tone "温柔、清晰、贴耳"

# 跑对话模式
python main.py dialogue
```

## 项目结构

```text
snowvoice-studio/
├── cli/                 # CLI 入口与命令
├── core/                # 语音引擎、模式调度、音频处理
├── configs/             # 运行配置与 personas 映射
├── assets/              # 参考音频、标准样音、产出音频
├── models/              # 本地模型目录
├── out/                 # 默认输出目录
└── qwen_tts/            # 上游模型适配代码
```

## 已有功能

### 1. 声音克隆

- 从已有角色样音出发生成新台词
- 优先复用 `assets/temp/` 中的标准样音
- 支持 `personas.json` 做角色映射

### 2. 音色设计

- 用文字描述直接生成新音色
- 可选择沉淀到标准样音库
- 适合先试听，再批量进入生产

### 3. 对话生成

- 支持多角色脚本
- 适合剧情对白、短剧、播客片段
- 当前入口仍是 `python main.py dialogue`

## 路线图

### Phase 1：命名与基础清理

- [x] 仓库统一改名为 `snowvoice-studio`
- [x] Python 包名统一为 `snowvoice-studio`
- [x] CLI 主入口统一为 `snowvoice`
- [x] README 改成对小白和 AI / agent 友好的表达

### Phase 2：CLI 稳定化

- [ ] 增加 `snowvoice doctor` 环境检查
- [ ] 增加 `snowvoice init` 一键初始化
- [ ] 补齐 `dialogue` 的 CLI 子命令
- [ ] 为常见报错提供更直接的提示

### Phase 3：WebUI MVP

- [ ] 本地上传参考音频
- [ ] 页面填写克隆 / 设计 / 对话参数
- [ ] 页面直接试听、下载和查看任务结果
- [ ] WebUI 与 CLI 共用同一套核心引擎

### Phase 4：Agent 自动化

- [ ] 提供无交互安装模式
- [ ] 提供稳定的任务输入 / 输出约定
- [ ] 让 agent 能自动发现模型、配置和产出目录
- [ ] 为自动化调用补最小可用文档与样例

## 适合谁用

- 想本地跑中文 TTS 的创作者
- 想把配音流程接给 AI 助手的个人开发者
- 想先从 CLI 跑通，再逐步接 WebUI 的小团队

## 开源说明

- License: [Apache-2.0](LICENSE)
- 上游基础：Qwen3-TTS
- 本项目定位：开源、本地优先、自动化友好

## 命令速查

完整命令请看 [docs/COMMANDS.md](docs/COMMANDS.md)。
