import os
import sys
from pydub import AudioSegment
from .engine import TTSBaseEngine
from .utils import get_persona_cn

class VoiceCloner(TTSBaseEngine):
    """【分支功能：声音克隆】 支持安全偏移裁剪、格式归一化及智能缓存"""
    
    def __init__(self, model_size="1.7B"):
        super().__init__("Base", model_size)
        self.ref_dir = os.path.join(self.base_dir, "assets/reference_audio")
        self.temp_dir = os.path.join(self.base_dir, "assets/temp")

    def _prepare_reference(self, audio_path, persona, max_sec=10, skip_start_ms=1500):
        """核心流转：跳过开头杂音，提取黄金人声片段并转为无损 WAV"""
        os.makedirs(self.temp_dir, exist_ok=True)
        
        persona_cn = get_persona_cn(persona)
        temp_name = f"当前参考_{persona_cn}.wav"
        temp_path = os.path.join(self.temp_dir, temp_name)
        
        # 智能缓存逻辑
        if os.path.exists(temp_path):
            if os.path.getmtime(temp_path) >= os.path.getmtime(audio_path):
                return temp_path
        
        print(f"🔨 正在为【{persona_cn}】提取纯净样音 (已跳过开头 {skip_start_ms/1000}s 杂音区)...")
        try:
            audio = AudioSegment.from_file(audio_path)
            
            # --- 【优化：安全偏移逻辑】 ---
            # 1. 自动跳过开头的 1.5s (skip_start_ms)
            if len(audio) > skip_start_ms + 2000: # 确保音频够长
                audio = audio[skip_start_ms:]
            
            # 2. 物理切除首尾多余静音
            def trim_silence(sound, threshold=-50.0, chunk_size=5):
                start_trim = 0
                while sound[start_trim:start_trim+chunk_size].dBFS < threshold and start_trim < len(sound):
                    start_trim += chunk_size
                end_trim = 0
                while sound[len(sound)-end_trim-chunk_size:len(sound)-end_trim].dBFS < threshold and end_trim < len(sound):
                    end_trim += chunk_size
                return sound[start_trim:len(sound)-end_trim]

            audio = trim_silence(audio)
            
            # 3. 截取黄金 10 秒
            duration_sec = len(audio) / 1000.0
            if duration_sec > max_sec:
                audio = audio[:max_sec * 1000]
            
            audio.export(temp_path, format="wav")
            return temp_path
        except Exception as e:
            print(f"⚠️ 样音处理失败: {e}，回退使用原始路径")
            return audio_path

    def process(self, text, persona, language, instruct):
        persona_cn = get_persona_cn(persona)
        
        # 扫描资产库
        possible_exts = [".wav", ".mp3", ".m4a"]
        ref_audio = None
        for name in [f"{persona_cn}_参考", f"{persona}_ref"]:
            for ext in possible_exts:
                path = os.path.join(self.ref_dir, name + ext)
                if os.path.exists(path):
                    ref_audio = path
                    break
            if ref_audio: break
        
        if not ref_audio:
            print(f"\n❌ 错误：找不到角色【{persona_cn}】的参考音频底稿！")
            sys.exit(1)
        
        processed_ref = self._prepare_reference(ref_audio, persona)
        print(f"👥 模式：声音克隆 | 物理参考源 (避障WAV)：{os.path.basename(processed_ref)}")
        
        return self.model.generate_voice_clone(
            text=text, 
            language=language, 
            ref_audio=processed_ref, 
            x_vector_only_mode=True
        )
