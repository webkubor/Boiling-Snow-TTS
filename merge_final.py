import os
from pydub import AudioSegment

BASE_DIR = "/Users/webkubor/Desktop/create/Qwen3-TTS"
REF_WAV = os.path.join(BASE_DIR, "assets/reference_audio/设计_水烟_极致软糯试音.wav")
GEN_WAV = os.path.join(BASE_DIR, "assets/output_audio/生成的下半场.wav")
FINAL_OUT = os.path.join(BASE_DIR, "assets/output_audio/场景_花楼破防版_终极合体.wav")

def merge():
    print("开始缝合原声与新对话...")
    # 1. 加载原声 (极致软糯试音)
    ref = AudioSegment.from_file(REF_WAV)
    
    # 2. 加载新生成的对话 (道士破防)
    gen = AudioSegment.from_file(GEN_WAV)
    
    # 3. 交叠缝合
    # 我们让第一句原声还没完事的时候，道士的“咳……”声已经进来了，更有现场感。
    overlap_ms = 400 
    gap_ms = 800
    
    # 先淡出一点点原声
    ref = ref.fade_out(200)
    
    # 缝合：原声 + (静音 - 重叠) + 新声
    # 或者直接 append 这种写法更简单
    combined = ref.append(gen, crossfade=overlap_ms)
    
    # 归一化并导出
    combined = combined.normalize(headroom=0.1)
    combined.export(FINAL_OUT, format="wav")
    print(f"✅ 合体成功！文件已存至：{FINAL_OUT}")

if __name__ == "__main__":
    merge()
