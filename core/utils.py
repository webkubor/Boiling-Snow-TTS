import os
import json
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONA_CONFIG = os.path.join(BASE_DIR, "configs/personas.json")

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
    return persona_map.get(persona_en, persona_en)

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_output_path(config, base_dir, suffix=""):
    content_type = config.get("content_type", "movie")
    out_dir = os.path.join(base_dir, "assets/podcast_output" if content_type == "podcast" else "assets/output_audio")
    os.makedirs(out_dir, exist_ok=True)
    if config.get("output_filename") and not suffix:
        return os.path.join(out_dir, config["output_filename"])
    persona_cn = get_persona_cn(config.get("persona", "多角色"))
    is_dial = "lines" in config and isinstance(config["lines"], list)
    mode_tag = "对话" if is_dial else ("设计" if config.get("model_type") == "VoiceDesign" else "克隆")
    filename = f"[{mode_tag}]{persona_cn}_第{config.get('episode', 'X')}集_{config.get('title', '未命名')}{suffix}.wav"
    return os.path.join(out_dir, re.sub(r'[\/:*?"<>|]', '_', filename))

def log_generation_metadata(config, audio_path, base_dir):
    """【路径优化版】将设计配方存入根目录 voice_designs/"""
    persona_en = config.get("persona", "unknown")
    persona_cn = get_persona_cn(persona_en)
    mode_type = config.get("model_type", "Base")
    
    # --- 分支 A：记录【音色设计配方】(存入根目录，方便调阅) ---
    if mode_type == "VoiceDesign":
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
        print(f"🧪 [设计配方] 已归档至显眼包目录：voice_designs/{persona_cn}.json")

    # --- 分支 B：记录【日常生成日志】(保留在 assets 内部) ---
    log_dir = os.path.join(base_dir, "assets/metadata/production_logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{persona_cn}_生成历史.json")
    
    new_log = {
        "audio_file": os.path.basename(audio_path),
        "text": config.get("text", "场景集锦"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_dialogue": "lines" in config
    }
    
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
