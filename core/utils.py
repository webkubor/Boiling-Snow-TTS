import os
import json
import re
from datetime import datetime

# 统一角色名映射表
PERSONA_MAP = {
    "narrator": "旁白",
    "xiao_jinxian": "萧烬弦",
    "gu_qiyue": "顾栖月",
    "mu_xige": "慕夕歌",
    "su_mengcheng": "苏梦城",
    "ouyang_kuangtu": "欧阳狂徒",
    "mu_beige": "慕北歌",
    "shadow": "影",
    "xie_wufeng": "谢无锋",
    "ye_chenzhou": "叶沉舟",
    "lu_tingchao": "陆听潮",
    "yan_zhaoling": "燕照绫",
    "ning_guanchen": "宁观尘"
}

def get_persona_cn(persona_en):
    return PERSONA_MAP.get(persona_en, persona_en)

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_output_path(config, base_dir):
    out_dir = os.path.join(base_dir, "assets/output_audio")
    os.makedirs(out_dir, exist_ok=True)
    
    if config.get("output_filename"):
        return os.path.join(out_dir, config["output_filename"])
    
    persona_cn = get_persona_cn(config.get("persona", "未知"))
    mode_tag = "设计" if config.get("model_type") == "VoiceDesign" else "克隆"
    
    filename = f"[{mode_tag}]{persona_cn}_第{config.get('episode', 'X')}集_{config.get('title', '未命名')}.wav"
    filename = re.sub(r'[\/:*?"<>|]', '_', filename)
    
    return os.path.join(out_dir, filename)

def log_generation_metadata(config, audio_path, base_dir):
    """【新增】为每个角色记录台词与音频的对应关系"""
    meta_dir = os.path.join(base_dir, "assets/metadata")
    os.makedirs(meta_dir, exist_ok=True)
    
    persona_en = config.get("persona", "unknown")
    persona_cn = get_persona_cn(persona_en)
    meta_file = os.path.join(meta_dir, f"{persona_cn}_台词记录.json")
    
    new_record = {
        "audio_file": os.path.basename(audio_path),
        "text": config.get("text", ""),
        "emotion": config.get("emotion", ""),
        "tone": config.get("tone", ""),
        "model_type": config.get("model_type", "Base"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data = {"persona": persona_cn, "records": []}
    if os.path.exists(meta_file):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            pass
            
    data["records"].append(new_record)
    
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"📄 台词记录已更新：assets/metadata/{persona_cn}_台词记录.json")
