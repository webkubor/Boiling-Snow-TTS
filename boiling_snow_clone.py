import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
import os
import json
import re
import sys

# 开启 Mac MPS 兼容性支持
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# --- 路径配置 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
REF_DIR = os.path.join(ASSETS_DIR, "reference_audio")
OUT_DIR = os.path.join(ASSETS_DIR, "output_audio")
CONFIG_PATH = os.path.join(BASE_DIR, "configs/config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ 错误：配置文件 {CONFIG_PATH} 不存在。")
        sys.exit(1)
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_device_info():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "mps" else torch.float32
    return device, dtype

def generate_filename(config):
    persona = config.get("persona", "narrator")
    episode = config.get("episode", "XX")
    title = config.get("title", "未命名")
    model_type = config.get("model_type", "Base")
    
    persona_map = {"narrator": "旁白", "xiao_jinxian": "萧烬弦", "gu_qiyue": "顾栖月", "mu_xige": "慕夕歌"}
    persona_cn = persona_map.get(persona, persona)
    
    # 构造：[模式]角色_第X集_标题
    mode_tag = "设计" if model_type == "VoiceDesign" else "克隆"
    name = f"[{mode_tag}]{persona_cn}_第{episode}集_{title}.wav"
    return re.sub(r'[\/:*?"<>|]', '_', name)

# --- 核心引擎类 ---
class BoilingSnowEngine:
    def __init__(self, model_type, model_size):
        self.model_type = model_type
        self.model_size = model_size
        self.device, self.dtype = get_device_info()
        self.model_path = os.path.join(BASE_DIR, f"models/{model_type}-{model_size}")
        
        if not os.path.exists(self.model_path):
            print(f"⚠️ 路径 {self.model_path} 不存在，回退到 Base-0.6B")
            self.model_path = os.path.join(BASE_DIR, "models/Base-0.6B")
            self.model_type = "Base"

        print(f"🚀 正在加载【{self.model_type}】引擎 ({self.model_size}) 到 {self.device.upper()}...")
        self.model = Qwen3TTSModel.from_pretrained(
            self.model_path,
            device_map=self.device,
            dtype=self.dtype,
            attn_implementation="sdpa"
        )

    def run_cloning(self, text, persona, language, instruct):
        """【模式 A】声音克隆：严格依赖参考音频"""
        ref_audio = os.path.join(REF_DIR, f"{persona}_ref.mp3")
        if not os.path.exists(ref_audio):
            print(f"⚠️ 参考音色 {persona} 不存在，使用默认说书人")
            ref_audio = os.path.join(REF_DIR, "narrator_ref.mp3")
        
        print(f"👥 模式：声音克隆 | 参考：{os.path.basename(ref_audio)} | 语气：{instruct}")
        return self.model.generate_voice_clone(
            text=text, language=language, ref_audio=ref_audio, x_vector_only_mode=True
        )

    def run_design(self, text, language, instruct):
        """【模式 B】音色设计：严格基于文字描述，不使用参考音频"""
        print(f"🎨 模式：音色设计 | 描述指令：{instruct}")
        return self.model.generate_voice_design(
            text=text, language=language, instruct=instruct
        )

    def run_preset(self, text, speaker, language, instruct):
        """【模式 C】预设音色：使用官方固定精品库"""
        print(f"👤 模式：预设音色 | 角色：{speaker} | 语气：{instruct}")
        return self.model.generate_custom_voice(
            text=text, speaker=speaker, language=language, instruct=instruct
        )

# --- 主程序 ---
if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    cfg = load_config()
    
    # 初始化隔离引擎
    engine = BoilingSnowEngine(cfg.get("model_type", "Base"), cfg.get("model_size", "1.7B"))
    
    # 提取参数
    text = cfg.get("text", "")
    lang = cfg.get("language", "Chinese")
    instruct = f"{cfg.get('tone', '')}，{cfg.get('emotion', '')}".strip("，")
    
    # 路由派发，确保逻辑完全隔离
    m_type = cfg.get("model_type", "Base")
    if m_type == "VoiceDesign":
        wavs, sr = engine.run_design(text, lang, instruct)
    elif m_type == "CustomVoice":
        wavs, sr = engine.run_preset(text, cfg.get("speaker", "Vivian"), lang, instruct)
    else:
        wavs, sr = engine.run_cloning(text, cfg.get("persona", "narrator"), lang, instruct)

    # 导出
    out_name = cfg.get("output_filename") or generate_filename(cfg)
    out_path = os.path.join(OUT_DIR, out_name)
    sf.write(out_path, wavs[0], sr)
    print(f"✨ 生成完成！江湖回响已存至：{out_path}")
