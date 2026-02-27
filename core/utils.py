import os
import json
import re
from datetime import datetime
from pydub import AudioSegment

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
    "ning_guanchen": "宁观尘",
    "me": "老爹",
    "yue_qizhou": "月栖洲"
}

def get_persona_cn(persona_en):
    return PERSONA_MAP.get(persona_en, persona_en)

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_output_path(config, base_dir):
    content_type = config.get("content_type", "movie")
    if content_type == "podcast":
        out_dir = os.path.join(base_dir, "assets/podcast_output")
    else:
        out_dir = os.path.join(base_dir, "assets/output_audio")
    os.makedirs(out_dir, exist_ok=True)
    
    if config.get("output_filename"):
        return os.path.join(out_dir, config["output_filename"])
    
    persona_cn = get_persona_cn(config.get("persona", "未知"))
    mode_tag = "设计" if config.get("model_type") == "VoiceDesign" else "克隆"
    
    if content_type == "podcast":
        filename = f"[播客]{config.get('title', '未命名专栏')}.wav"
    else:
        filename = f"[{mode_tag}]{persona_cn}_第{config.get('episode', 'X')}集_{config.get('title', '未命名')}.wav"
    return os.path.join(out_dir, re.sub(r'[\/:*?"<>|]', '_', filename))

def post_process_audio(input_path, content_type="movie"):
    """【新增】播客级后期处理：增加首尾留白、音量标准化、清晰度增强"""
    print(f"🪄 正在执行后期调音 (模式: {content_type})...")
    try:
        audio = AudioSegment.from_file(input_path)
        
        # 1. 声音标准化（让声音更“贴耳”、更清晰）
        audio = audio.normalize(headroom=0.1)
        
        if content_type == "podcast":
            # 2. 播客专属：首留白 1.5s，尾留白 1s
            silence_start = AudioSegment.silent(duration=1500)
            silence_end = AudioSegment.silent(duration=1000)
            audio = silence_start + audio + silence_end
            print("⏳ 已加入 1.5s 开场留白...")
            
        audio.export(input_path, format="wav")
        return True
    except Exception as e:
        print(f"⚠️ 后期调音失败: {e}")
        return False

def log_generation_metadata(config, audio_path, base_dir):
    meta_dir = os.path.join(base_dir, "assets/metadata")
    os.makedirs(meta_dir, exist_ok=True)
    persona_cn = get_persona_cn(config.get("persona", "unknown"))
    meta_file = os.path.join(meta_dir, f"{persona_cn}_台词记录.json")
    
    new_record = {
        "audio_file": os.path.basename(audio_path),
        "text": config.get("text", ""),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    data = {"persona": persona_cn, "records": []}
    if os.path.exists(meta_file):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except: pass
    data["records"].append(new_record)
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
