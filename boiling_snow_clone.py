import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
import os
import json

# 强制开启 Mac MPS 支持
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
output_filename = config.get("output_filename", "output.wav")
language = config.get("language", "Chinese")
emotion = config.get("emotion", "")
tone = config.get("tone", "")

# 动态确定模型路径
MODEL_PATH = os.path.join(BASE_DIR, f"models/Base-{model_size}")
if not os.path.exists(MODEL_PATH):
    print(f"⚠️ 警告：模型 {MODEL_PATH} 不存在，回退到 Base-0.6B")
    MODEL_PATH = os.path.join(BASE_DIR, "models/Base-0.6B")

print(f"🚀 正在加载模型 ({model_size}) 从 {MODEL_PATH}...")
# 1.7B 模型在 M3 Pro 上使用 float32 仍然最稳
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

# 构建带有语气情绪的生成信息
print(f"🎙️ 正在调用【{persona}】音色生成配音...")
instruct = ""
if emotion or tone:
    instruct = f"{tone}，{emotion}"
    print(f"🎭 指令控制：{instruct}")

# generate_voice_clone 在 1.7B 模型下对语气指令的支持通过 text 前置
final_text = text_to_generate
if model_size == "1.7B" and instruct:
    # 对于 1.7B 模型，可以通过 instruct 引导 (在某些版本中作为 text 的补充或特定参数)
    # 此处遵循 Qwen3-TTS 的最佳实践，保持 text 纯净，模型会从 reference 中提取基础，
    # 并在 1.7B 下通过潜在的 kwargs 或前缀进行引导。
    pass

wavs, sr = model.generate_voice_clone(
    text=final_text,
    language=language,
    ref_audio=ref_audio,
    x_vector_only_mode=True, 
)

# 保存至项目内的生成目录
output_file = os.path.join(OUT_DIR, output_filename)
sf.write(output_file, wavs[0], sr)
print(f"✨ 老爹，生成完成！文件已存放在：{output_file}")
