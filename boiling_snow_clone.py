import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel
import os

# 强制开启 Mac MPS 支持
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

print("🚀 正在加载模型 (Base-0.6B) 到 CPU...")
model = Qwen3TTSModel.from_pretrained(
    "/Users/webkubor/Desktop/Qwen3-TTS/models/Base-0.6B",
    device_map="cpu",  # 暂时改回 CPU 以解决 MPS 下的稳定性问题
    dtype=torch.float32 # CPU 上 float32 更稳定
)

# 使用项目资产目录管理
# 旁白/说书人音色参考：assets/reference_audio/narration_narrator_ref.mp3 (原 xiaojinxuan_ref.mp3)
# 自动剪裁逻辑已在内存中记录，此处固定路径

ASSETS_DIR = "/Users/webkubor/Desktop/Qwen3-TTS/assets"
REF_DIR = os.path.join(ASSETS_DIR, "reference_audio")
OUT_DIR = os.path.join(ASSETS_DIR, "output_audio")

# 确保输出目录存在
os.makedirs(OUT_DIR, exist_ok=True)

# 默认说书人/旁白参考音频
ref_audio = os.path.join(REF_DIR, "narrator_ref.mp3") 

print(f"🎙️ 正在调用【说书人】音色 ({ref_audio}) 进行旁白生成...")
wavs, sr = model.generate_voice_clone(
    text="江湖路远，雪落无声。这沸腾之雪，终究还是要由我们来续写。",
    language="Chinese",
    ref_audio=ref_audio,
    x_vector_only_mode=True, 
)

# 旁白成品存放在 output_audio 目录
output_filename = "narrator_boiling_snow_intro.wav"
output_file = os.path.join(OUT_DIR, output_filename)
sf.write(output_file, wavs[0], sr)
print(f"✨ 老爹，克隆完成！文件已存放在项目生成目录：{output_file}")
