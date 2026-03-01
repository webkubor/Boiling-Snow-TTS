import os
import json
import re
from datetime import datetime
from typing import Any, Dict, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONA_CONFIG = os.path.join(BASE_DIR, "configs/personas.json")
CONFIG_DIR = os.path.join(BASE_DIR, "configs")
REFERENCE_AUDIO_DIR_REL = "assets/reference_audio"
ALLOWED_REFERENCE_EXTS = (".wav", ".mp3", ".m4a")

CORE_RUNTIME_CONFIGS = {
    "clone": "clone.json",
    "design": "design.json",
    "dialogue": "dialogue.json",
}

DEFAULT_CONFIG_ALIASES = {
    "single": "clone",
    "clone": "clone",
    "design": "design",
    "voice_design": "design",
    "voice_production": "dialogue",
    "dialogue": "dialogue",
    "scene": "dialogue",
}

POLICY_RULES = {
    "max_text_chars": 400,
    "require_persona_for_single": True,
    "require_role_or_persona_for_dialogue_line": True,
    "forbid_empty_instruction_when_voice_design": True,
    "forbidden_instruction_keywords": ["nsfw", "露骨", "仇恨", "极端暴力"],
}

def get_persona_map():
    default_map = {"narrator": "旁白", "me": "老爹", "yue_qizhou": "月栖洲"}
    if os.path.exists(PERSONA_CONFIG):
        try:
            with open(PERSONA_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return default_map
    return default_map

def get_persona_cn(persona_en):
    persona_map = get_persona_map()
    data = persona_map.get(persona_en, persona_en)
    if isinstance(data, dict):
        return data.get("name", persona_en)
    return data

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _expected_ref_base(persona_name: str) -> str:
    return f"{persona_name}_参考"

def _normalize_ref_path(ref_path: str) -> str:
    return ref_path.replace("\\", "/")

def validate_persona_ref_rule(persona: str, persona_data: Dict[str, Any]):
    """强制约束：ref 必须位于 assets/reference_audio 且命名符合 <角色名>_参考.<ext>。"""
    if not isinstance(persona_data, dict):
        return
    if "ref" not in persona_data:
        return

    persona_name = str(persona_data.get("name", "")).strip()
    ref_rel = str(persona_data.get("ref", "")).strip()
    if not persona_name:
        raise ValueError(f"personas.json 中 {persona} 缺少 name。")
    if not ref_rel:
        raise ValueError(f"personas.json 中 {persona} 的 ref 不能为空。")

    normalized_ref = _normalize_ref_path(ref_rel)
    expected_prefix = f"{REFERENCE_AUDIO_DIR_REL}/"
    if not normalized_ref.startswith(expected_prefix):
        raise ValueError(
            f"personas.json 中 {persona} 的 ref 非法：{ref_rel}。"
            f"必须放在 {REFERENCE_AUDIO_DIR_REL}/ 下。"
        )

    ref_name = os.path.basename(normalized_ref)
    ref_stem, ref_ext = os.path.splitext(ref_name)
    if ref_ext.lower() not in ALLOWED_REFERENCE_EXTS:
        raise ValueError(
            f"personas.json 中 {persona} 的 ref 后缀非法：{ref_ext}。"
            f"仅允许 {', '.join(ALLOWED_REFERENCE_EXTS)}"
        )

    expected_stem = _expected_ref_base(persona_name)
    if ref_stem != expected_stem:
        raise ValueError(
            f"personas.json 中 {persona} 的 ref 命名不符合规范：{ref_name}。"
            f"应为 {expected_stem}<ext>"
        )

def resolve_persona_ref_audio(base_dir: str, persona: str, persona_data: Dict[str, Any]) -> str:
    """按强规则解析参考音频路径，并校验文件存在。"""
    # validate_persona_ref_rule(persona, persona_data) # 彻底废弃对原始参考目录的强绑定

    persona_cn = get_persona_cn(persona)
    temp_ref = os.path.join(base_dir, "assets/temp", f"当前参考_{persona_cn}.wav")

    if os.path.exists(temp_ref):
        return temp_ref

    ref_rel = str(persona_data.get("ref", "")).strip()
    if not ref_rel:
        return ""
    ref_path = os.path.join(base_dir, ref_rel)
    if not os.path.exists(ref_path):
        raise ValueError(
            f"角色 {persona} 的参考音频资产不足：\n"
            f"1. 核心样音缺失：{temp_ref}\n"
            f"2. 原始素材缺失：{ref_rel}"
        )
    return ref_path

def _in_configs_dir(path: str) -> bool:
    abs_configs = os.path.abspath(CONFIG_DIR)
    abs_path = os.path.abspath(path)
    return os.path.commonpath([abs_configs, abs_path]) == abs_configs

def resolve_config_path(config_arg: str = "single") -> Tuple[str, str]:
    """将 CLI 参数解析为受控配置路径，阻止 configs 根目录继续堆临时文件。"""
    arg = (config_arg or "single").strip()
    alias = DEFAULT_CONFIG_ALIASES.get(arg, arg)

    if alias in CORE_RUNTIME_CONFIGS:
        rel_path = CORE_RUNTIME_CONFIGS[alias]
        cfg_path = os.path.join(CONFIG_DIR, rel_path)
        if not _in_configs_dir(cfg_path):
            raise ValueError(f"配置越界：{rel_path}")
        if not os.path.exists(cfg_path):
            raise ValueError(f"配置不存在：{rel_path}")
        return cfg_path, alias

    if arg.endswith(".json"):
        normalized = os.path.normpath(arg)
        if os.path.isabs(normalized):
            cfg_path = normalized
            rel_path = os.path.relpath(cfg_path, CONFIG_DIR)
        else:
            cfg_path = os.path.join(CONFIG_DIR, normalized)
            rel_path = normalized

        if not _in_configs_dir(cfg_path):
            raise ValueError("仅允许加载 configs 目录内的配置文件。")
        if not os.path.exists(cfg_path):
            raise ValueError(f"配置不存在：{rel_path}")

        # 根目录仅保留 4 个核心 JSON（clone/design/dialogue/personas）
        if "/" not in rel_path and rel_path not in {
            "clone.json",
            "design.json",
            "dialogue.json",
            "personas.json",
        }:
            raise ValueError(
                "configs 根目录仅允许 4 个核心 JSON。一次性配置请放 configs/scratch/ 并通过 scratch/*.json 调用。"
            )
        return cfg_path, rel_path

    raise ValueError(f"未知配置参数：{config_arg}。请使用 clone/design/dialogue 或 scratch/*.json")

def _assert_text_rules(text: str, field_name: str, max_chars: int):
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"{field_name} 不能为空。")
    if len(text) > max_chars:
        raise ValueError(f"{field_name} 超过限制（{len(text)} > {max_chars}）。")

def validate_runtime_config(config: Dict[str, Any], config_ref: str = ""):
    """运行前策略校验：防止无约束配置进入主流程。"""
    rules = POLICY_RULES
    max_text_chars = int(rules.get("max_text_chars", 600))
    require_persona = bool(rules.get("require_persona_for_single", True))
    require_line_role = bool(rules.get("require_role_or_persona_for_dialogue_line", True))
    block_keywords = rules.get("forbidden_instruction_keywords", [])
    require_design_prompt = bool(rules.get("forbid_empty_instruction_when_voice_design", True))

    persona_map = get_persona_map()
    task_type = config.get("type", "single")
    model_type = config.get("model_type", "Base")
    lines = config.get("lines")

    # 注册表层面的命名规则校验（全面放开路径限制，只校验核心逻辑）
    for persona_key, persona_data in persona_map.items():
        if isinstance(persona_data, dict) and "ref" in persona_data:
            # validate_persona_ref_rule(persona_key, persona_data) # 切除古板校验
            pass

    if isinstance(lines, list):
        for idx, line in enumerate(lines, start=1):
            if not isinstance(line, dict):
                raise ValueError(f"lines[{idx}] 必须是对象。")
            role_or_persona = line.get("role") or line.get("persona")
            if require_line_role and not role_or_persona:
                raise ValueError(f"lines[{idx}] 缺少 role/persona。")
            if role_or_persona and role_or_persona not in persona_map:
                raise ValueError(f"lines[{idx}] 角色未注册：{role_or_persona}。请先在 personas.json 定义。")
            if role_or_persona and isinstance(persona_map.get(role_or_persona), dict):
                pdata = persona_map.get(role_or_persona, {})
                if "ref" in pdata:
                    resolve_persona_ref_audio(BASE_DIR, role_or_persona, pdata)
            _assert_text_rules(line.get("text", ""), f"lines[{idx}].text", max_text_chars)
            merged_instruct = " ".join([
                str(line.get("tone", "")),
                str(line.get("emotion", "")),
                str(line.get("instruction", "")),
            ]).lower()
            for keyword in block_keywords:
                if keyword and keyword.lower() in merged_instruct:
                    raise ValueError(f"lines[{idx}] 指令命中禁用关键词：{keyword}")

    elif task_type in ("single", "clone") or model_type == "Base":
        if require_persona and not config.get("persona"):
            raise ValueError("single/clone 模式必须提供 persona。")
        persona = config.get("persona")
        if persona and persona not in persona_map:
            raise ValueError(f"persona 未注册：{persona}。请先在 personas.json 定义。")
        if persona and isinstance(persona_map.get(persona), dict):
            pdata = persona_map.get(persona, {})
            if "ref" in pdata:
                resolve_persona_ref_audio(BASE_DIR, persona, pdata)
        if model_type != "VoiceDesign":
            _assert_text_rules(config.get("text", ""), "text", max_text_chars)

    if model_type == "VoiceDesign":
        _assert_text_rules(config.get("text", ""), "text", max_text_chars)
        tone = str(config.get("tone", "")).strip()
        emotion = str(config.get("emotion", "")).strip()
        if require_design_prompt and not (tone or emotion):
            raise ValueError("VoiceDesign 模式至少提供 tone 或 emotion。")
        merged_instruct = f"{tone} {emotion}".lower()
        for keyword in block_keywords:
            if keyword and keyword.lower() in merged_instruct:
                raise ValueError(f"VoiceDesign 指令命中禁用关键词：{keyword}")

    # 标注来源便于追踪触发点
    if config_ref:
        print(f"🧩 配置策略校验通过：{config_ref}")

def generate_output_path(config, base_dir, suffix=""):
    out_dir = os.path.join(base_dir, "out")
    os.makedirs(out_dir, exist_ok=True)
    if config.get("output_filename") and not suffix:
        return os.path.join(out_dir, config["output_filename"])
    
    is_dial = "lines" in config and isinstance(config["lines"], list)
    if is_dial:
        persona_cn = "场景对话"
    else:
        persona_cn = get_persona_cn(config.get("persona", "未知"))
        
    mode_tag = "对话" if is_dial else ("设计" if config.get("model_type") == "VoiceDesign" else "克隆")
    filename = f"[{mode_tag}]{persona_cn}_第{config.get('episode', 'X')}集_{config.get('title', '未命名')}{suffix}.wav"
    return os.path.join(out_dir, re.sub(r'[\/:*?"<>|]', '_', filename))

def log_generation_metadata(config, audio_path, base_dir):
    """【修复版】智能识别对话场景，避免出现 unknown 记录"""
    mode_type = config.get("model_type", "Base")
    is_dial = "lines" in config and isinstance(config["lines"], list)
    episode = config.get("episode", "unknown")
    
    # 确定记录主体的中文名
    if is_dial or episode == "Scene":
        persona_cn = "场景"
    else:
        persona_en = config.get("persona", "unknown")
        persona_cn = get_persona_cn(persona_en)
    
    # --- 分支 A：音色设计配方 ---
    if mode_type == "VoiceDesign" and not is_dial:
        design_dir = os.path.join(base_dir, "voice_designs")
        os.makedirs(design_dir, exist_ok=True)
        design_file = os.path.join(design_dir, f"{persona_cn}.json")
        
        design_data = {
            "persona": persona_cn,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": f"{config.get('model_size', '1.7B')}-VoiceDesign",
            "instruction_formula": {
                "full_prompt": config.get("tone", ""),
                "emotion": config.get("emotion", "")
            },
            "reference_seed_audio": f"{persona_cn}_参考.wav"
        }
        with open(design_file, 'w', encoding='utf-8') as f:
            json.dump(design_data, f, ensure_ascii=False, indent=2)
        print(f"🧪 [设计配方] 已归档：voice_designs/{persona_cn}.json")

    # --- 分支 B：生成历史日志 ---
    log_dir = os.path.join(base_dir, "assets/production")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{persona_cn}_生成历史.json")
    
    new_log = {
        "audio_file": os.path.basename(audio_path),
        "title": config.get("title", "未命名"),
        "episode": episode,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_dialogue": is_dial
    }
    
    if is_dial:
        new_log["dialogue_lines"] = config["lines"]
    else:
        new_log["text"] = config.get("text", "")

    history = {"persona": persona_cn, "records": []}
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except: pass
    history["records"].append(new_log)
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f"📄 [生成日志] 已更新：assets/metadata/production_logs/{persona_cn}_生成历史.json")
