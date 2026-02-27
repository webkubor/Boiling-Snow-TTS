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

# 使用我为您提取的 8秒 萧烬弦参考音频
ref_audio = "/Users/webkubor/Desktop/Qwen3-TTS/assets/reference_audio/xiaojinxuan_ref.mp3"

print("🎙️ 正在进行声音克隆生成...")
wavs, sr = model.generate_voice_clone(
    text="江湖路远，雪落无声。我是萧烬弦，这沸腾之雪，终究还是要由我们来续写。",
    language="Chinese",
    ref_audio=ref_audio,
    x_vector_only_mode=True,  # 开启仅使用音色向量模式，不需要参考文本
)

output_file = "/Users/webkubor/Desktop/萧烬弦_克隆测试.wav"
sf.write(output_file, wavs[0], sr)
print(f"✨ 老爹，克隆完成！文件已存放在您的桌面：{output_file}")
