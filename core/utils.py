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
    "yue_qizhou": "月栖洲",
    "xiao_mo": "小墨"
}

def get_persona_cn(persona_en):
    return PERSONA_MAP.get(persona_en, persona_en)

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

def post_process_audio(input_path, content_type="movie", add_padding=True):
    try:
        audio = AudioSegment.from_file(input_path)
        audio = trim_silence_manually(audio)
        audio = audio.normalize(headroom=0.1).fade_in(50).fade_out(50)
        
        if add_padding:
            silence_start = AudioSegment.silent(duration=1500)
            silence_end = AudioSegment.silent(duration=1000)
            audio = silence_start + audio + silence_end
            
        audio.export(input_path, format="wav")
        return audio
    except Exception as e:
        print(f"⚠️ 后期调音失败: {e}")
        return None

def merge_dialogue(segments, output_path, gap_ms=800):
    print(f"🧵 正在缝合对话剧情 (角色间隔: {gap_ms}ms)...")
    combined = AudioSegment.silent(duration=1500)
    for i, seg in enumerate(segments):
        combined += seg
        if i < len(segments) - 1:
            combined += AudioSegment.silent(duration=gap_ms)
    combined += AudioSegment.silent(duration=1000)
    combined.export(output_path, format="wav")
    print(f"✅ 对话场景缝合完成！")

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
