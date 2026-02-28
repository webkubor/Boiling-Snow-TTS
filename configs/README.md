# Configs 治理说明

## 目录分层
- `configs/*.json`：仅保留 4 个核心 JSON：
  - `clone.json`
  - `design.json`
  - `dialogue.json`
  - `personas.json`
- `configs/scratch/*.json`：一次性调试配置（临时实验、单次修复验证）。

## 调用方式
- 推荐：`python main.py clone|design|dialogue`
- 指定临时配置：`python main.py scratch/temp_demo.json`

## 规则
- 根目录不再接受额外临时 JSON。
- 运行前会执行内置策略校验（字段完整性、文本长度、角色合法性、禁用关键词）。
- 角色必须在 `personas.json` 中注册。
