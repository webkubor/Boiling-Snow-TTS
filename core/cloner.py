import os
from pydub import AudioSegment
from .engine import TTSBaseEngine

class VoiceCloner(TTSBaseEngine):
    """【分支功能：声音克隆】 严格依赖参考音频，支持 AI 自动裁剪"""
    
    def __init__(self, model_size="1.7B"):
        super().__init__("Base", model_size)
        self.ref_dir = os.path.join(self.base_dir, "assets/reference_audio")
        self.temp_dir = os.path.join(self.base_dir, "assets/temp")

    def _auto_clip(self, audio_path, max_sec=10):
        """自动化处理：裁剪参考音频至黄金时长"""
        os.makedirs(self.temp_dir, exist_ok=True)
        try:
            audio = AudioSegment.from_file(audio_path)
            if len(audio) > max_sec * 1000:
                print(f"✂️ AI 自动剪辑：参考音频过长，正在截取前 {max_sec}s...")
                clipped = audio[:max_sec * 1000]
                temp_path = os.path.join(self.temp_dir, f"clipped_{os.path.basename(audio_path)}")
                clipped.export(temp_path, format="mp3")
                return temp_path
            return audio_path
        except Exception as e:
            print(f"⚠️ 自动剪辑跳过: {e}")
            return audio_path

    def process(self, text, persona, language, instruct):
        ref_audio = os.path.join(self.ref_dir, f"{persona}_ref.mp3")
        if not os.path.exists(ref_audio):
            print(f"⚠️ 参考音色 {persona} 不存在，回退至说书人")
            ref_audio = os.path.join(self.ref_dir, "narrator_ref.mp3")
        
        processed_ref = self._auto_clip(ref_audio)
        print(f"👥 模式：声音克隆 | 参考源：{os.path.basename(processed_ref)}")
        
        return self.model.generate_voice_clone(
            text=text, 
            language=language, 
            ref_audio=processed_ref, 
            x_vector_only_mode=True
        )
