import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
import os
import json
import re

# 开启 Mac MPS 兼容性支持
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# 获取基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
REF_DIR = os.path.join(ASSETS_DIR, "reference_audio")
OUT_DIR = os.path.join(ASSETS_DIR, "output_audio")
CONFIG_PATH = os.path.join(BASE_DIR, "configs/config.json")

# 确保输出目录存在
os.makedirs(OUT_DIR, exist_ok=True)

# 加载配置
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

text_to_generate = config.get("text", "")
persona = config.get("persona", "narrator")
model_size = config.get("model_size", "0.6B")
language = config.get("language", "Chinese")
emotion = config.get("emotion", "")
tone = config.get("tone", "")
episode = config.get("episode", "")
title = config.get("title", "")

# 动态生成中文文件名
persona_map = {
    "narrator": "旁白",
    "xiao_jinxian": "萧烬弦",
    "gu_qiyue": "顾栖月",
    "mu_xige": "慕夕歌"
}
persona_cn = persona_map.get(persona, persona)
output_filename = config.get("output_filename")
if not output_filename:
    output_filename = f"{persona_cn}_第{episode}集_{title}.wav"

output_filename = re.sub(r'[\/:*?"<>|]', '_', output_filename)
if not output_filename.endswith(".wav"):
    output_filename += ".wav"

# 动态确定模型路径
MODEL_PATH = os.path.join(BASE_DIR, f"models/Base-{model_size}")
if not os.path.exists(MODEL_PATH):
    print(f"⚠️ 警告：模型 {MODEL_PATH} 不存在，回退到 Base-0.6B")
    MODEL_PATH = os.path.join(BASE_DIR, "models/Base-0.6B")

# 探测设备：优先 MPS (GPU) 以利用 M3 Pro 性能
device = "mps" if torch.backends.mps.is_available() else "cpu"
dtype = torch.bfloat16 if device == "mps" else torch.float32

print(f"🚀 正在加载模型 ({model_size}) 到 {device.upper()}，精度: {dtype}...")

try:
    model = Qwen3TTSModel.from_pretrained(
        MODEL_PATH,
        device_map=device,
        dtype=dtype,
        # 使用 SDPA (Mac 原生加速)，消除 flash-attn 警告并提升速度
        attn_implementation="sdpa" 
    )
except Exception as e:
    print(f"⚠️ MPS 加速启动失败，正在回退到 CPU 模式... (原因: {e})")
    model = Qwen3TTSModel.from_pretrained(
        MODEL_PATH,
        device_map="cpu",
        dtype=torch.float32
    )

# 动态确定参考音频路径
ref_audio_name = f"{persona}_ref.mp3"
ref_audio = os.path.join(REF_DIR, ref_audio_name)

if not os.path.exists(ref_audio):
    print(f"⚠️ 警告：参考音频 {ref_audio} 不存在，将使用默认 narrator_ref.mp3")
    ref_audio = os.path.join(REF_DIR, "narrator_ref.mp3")

print(f"🎙️ 正在调用【{persona_cn}】音色生成配音...")
if emotion or tone:
    print(f"🎭 指令控制：{tone} | {emotion}")

wavs, sr = model.generate_voice_clone(
    text=text_to_generate,
    language=language,
    ref_audio=ref_audio,
    x_vector_only_mode=True, 
)

# 保存至项目内的生成目录
output_file = os.path.join(OUT_DIR, output_filename)
sf.write(output_file, wavs[0], sr)
print(f"✨ 老爹，生成完成！文件已存放在：{output_file}")
