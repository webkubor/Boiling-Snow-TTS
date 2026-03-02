# 命令速查 (Command Reference)

本文档用于统一说明本项目常用命令，避免“会用功能但找不到命令”。

## 1. 初始化与依赖安装

```bash
# 一键安装 Python 环境与模型
chmod +x install.sh && ./install.sh

# 激活虚拟环境
source .venv/bin/activate

# 安装 Python 包（含 web_api 依赖）
pip install -e .

# 安装 WebUI 前端依赖
npm --prefix webui install
```

## 2. AI 门禁与 Git Hook

```bash
# 校验 AI 初始化结构
npm run ai:check

# 安装提交前检查 hook
npm run hooks:install
```

## 3. CLI 生成命令

```bash
# 默认（等价 clone）
python main.py

# 克隆模式
python main.py clone

# 音色设计模式
python main.py design

# 对话模式
python main.py dialogue
```

说明：
- `python main.py design` 必须填写 `voice_name`。
- 设计默认仅输出到 `out/`（试听阶段）。
- 确认满意后把 `commit_to_temp` 设为 `true`，再执行一次 `python main.py design`，会同时：
  - 沉淀 `assets/temp/当前参考_<voice_name>.wav`
  - 更新 `configs/personas.json` 映射
  - 生成 `configs/generated/<voice_name>_generate.json`
- 设计文案最多 45 字；可留空，系统自动填默认短句（设计重点是音色 prompt）。
- 对话与常规生成默认使用 `assets/temp/` 的标准样音。
- 0-1 克隆阶段可在 `configs/clone.json` 里传入 `reference_audio`（原始参考音频路径），无需先注册 `personas.json`。
- 0-1 克隆阶段如果不填 `persona`，输出文件名会回退为 `reference_audio` 的文件名（去扩展名）。

## 4. WebUI 启动命令

```bash
# 终端 1：启动 FastAPI
npm run api:dev

# 终端 2：启动 React WebUI
npm run web:dev
```

访问地址：`http://127.0.0.1:5173`

## 5. 构建与检查

```bash
# 前端生产构建
npm run web:build

# 后端语法检查
.venv/bin/python -m py_compile web_api.py
```

## 6. 常见问题排查命令

```bash
# 看端口占用（API）
lsof -i :8000

# 看端口占用（WebUI）
lsof -i :5173

# 查看 Git 当前状态
git status --short
```
