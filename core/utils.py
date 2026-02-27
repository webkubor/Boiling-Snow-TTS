import os
import json
import re

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_output_path(config, base_dir):
    out_dir = os.path.join(base_dir, "assets/output_audio")
    os.makedirs(out_dir, exist_ok=True)
    
    # 优先从配置读取文件名
    if config.get("output_filename"):
        return os.path.join(out_dir, config["output_filename"])
    
    # 自动拼接中文名
    persona_map = {"narrator": "旁白", "xiao_jinxian": "萧烬弦", "gu_qiyue": "顾栖月", "mu_xige": "慕夕歌"}
    persona_cn = persona_map.get(config.get("persona"), config.get("persona", "未知"))
    mode_tag = "设计" if config.get("model_type") == "VoiceDesign" else "克隆"
    
    filename = f"[{mode_tag}]{persona_cn}_第{config.get('episode', 'X')}集_{config.get('title', '未命名')}.wav"
    filename = re.sub(r'[\/:*?"<>|]', '_', filename)
    
    return os.path.join(out_dir, filename)
