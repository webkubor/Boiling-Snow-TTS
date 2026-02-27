import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
import os
import json

# 强制开启 Mac MPS 支持
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# 获取基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models/Base-0.6B")
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
output_filename = config.get("output_filename", "output.wav")
language = config.get("language", "Chinese")

print(f"🚀 正在加载模型 (Base-0.6B) 从 {MODEL_PATH}...")
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

print(f"🎙️ 正在调用【{persona}】音色生成配音...")
print(f"📝 文案内容：{text_to_generate}")

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
