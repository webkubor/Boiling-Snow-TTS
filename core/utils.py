import os
import json
import re
from datetime import datetime
from pydub import AudioSegment

# 获取基础目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONA_CONFIG = os.path.join(BASE_DIR, "configs/personas.json")

def get_persona_map():
    """从本地 JSON 加载角色映射表，若不存在则返回基础映射"""
    default_map = {"narrator": "旁白", "me": "老爹", "yue_qizhou": "月栖洲"}
    if os.path.exists(PERSONA_CONFIG):
        try:
            with open(PERSONA_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_map
    return default_map

def get_persona_cn(persona_en):
    persona_map = get_persona_map()
    return persona_map.get(persona_en, persona_en)

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_output_path(config, base_dir, suffix=""):
    content_type = config.get("content_type", "movie")
    if content_type == "podcast":
        out_dir = os.path.join(base_dir, "assets/podcast_output")
    else:
        out_dir = os.path.join(base_dir, "assets/output_audio")
    os.makedirs(out_dir, exist_ok=True)
    
    if config.get("output_filename"):
        return os.path.join(out_dir, config["output_filename"])
    
    persona_cn = get_persona_cn(config.get("persona", "多角色"))
    is_dial = "lines" in config and isinstance(config["lines"], list)
    mode_tag = "对话" if is_dial else ("设计" if config.get("model_type") == "VoiceDesign" else "克隆")
    
    filename = f"[{mode_tag}]{persona_cn}_第{config.get('episode', 'X')}集_{config.get('title', '未命名')}{suffix}.wav"
    return os.path.join(out_dir, re.sub(r'[\/:*?"<>|]', '_', filename))

def trim_silence_manually(audio, threshold=-50.0, chunk_size=5):
    def detect_leading_silence(sound):
        iterate = 0
        while iterate < len(sound) and sound[iterate:iterate+chunk_size].dBFS < threshold:
            iterate += chunk_size
        return iterate
    start_idx = detect_leading_silence(audio)
    end_idx = detect_leading_silence(audio.reverse())
    return audio[start_idx : (len(audio) - end_idx)]

def post_process_audio(input_path, content_type="movie", add_padding=False):
    """后期调音：已去除强制静音留白，实现直接开嗓"""
    try:
        audio = AudioSegment.from_file(input_path)
        audio = trim_silence_manually(audio)
        audio = audio.normalize(headroom=0.1).fade_in(50).fade_out(50)
        audio.export(input_path, format="wav")
        return audio
    except Exception as e:
        print(f"⚠️ 后期调音失败: {e}")
        return None

def merge_dialogue(segments, output_path, gap_ms=800):
    print(f"🧵 正在缝合剧情 (无预留白直接开启)...")
    combined = AudioSegment.empty()
    for i, seg in enumerate(segments):
        combined += seg
        if i < len(segments) - 1:
            combined += AudioSegment.silent(duration=gap_ms)
    combined.export(output_path, format="wav")
    print(f"✅ 场景缝合完成！")

def log_generation_metadata(config, audio_path, base_dir):
    meta_dir = os.path.join(base_dir, "assets/metadata")
    os.makedirs(meta_dir, exist_ok=True)
    persona_cn = get_persona_cn(config.get("persona", "unknown"))
    meta_file = os.path.join(meta_dir, f"{persona_cn}_台词记录.json")
    
    new_record = {
        "audio_file": os.path.basename(audio_path),
        "text": config.get("text", "对话集锦"),
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
