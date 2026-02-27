import os
from pydub import AudioSegment
from .engine import TTSBaseEngine
from .utils import get_persona_cn

class VoiceCloner(TTSBaseEngine):
    """【分支功能：声音克隆】 严格依赖参考音频，支持 AI 自动裁剪"""
    
    def __init__(self, model_size="1.7B"):
        super().__init__("Base", model_size)
        self.ref_dir = os.path.join(self.base_dir, "assets/reference_audio")
        self.temp_dir = os.path.join(self.base_dir, "assets/temp")

    def _prepare_reference(self, audio_path, persona, max_sec=10):
        """核心流转：将最终使用的参考音频以中文名存入 temp 目录"""
        os.makedirs(self.temp_dir, exist_ok=True)
        
        persona_cn = get_persona_cn(persona)
        # 统一命名格式：当前参考_角色名.mp3
        temp_name = f"当前参考_{persona_cn}.mp3"
        temp_path = os.path.join(self.temp_dir, temp_name)
        
        try:
            audio = AudioSegment.from_file(audio_path)
            duration_sec = len(audio) / 1000.0
            
            if duration_sec > max_sec:
                print(f"✂️ AI 自动剪辑：参考音频过长 ({duration_sec:.1f}s)，正在截取前 {max_sec}s...")
                audio = audio[:max_sec * 1000]
            
            # 导出到 temp 目录
            audio.export(temp_path, format="mp3")
            return temp_path
        except Exception as e:
            print(f"⚠️ 样音流转失败: {e}，回退使用原始路径")
            return audio_path

    def process(self, text, persona, language, instruct):
        persona_cn = get_persona_cn(persona)
        
        # 寻找参考音频，优先找中文名的参考文件
        # 支持 {角色名}_参考.wav, {角色名}_参考.mp3, {persona}_ref.mp3 等格式
        possible_paths = [
            os.path.join(self.ref_dir, f"{persona_cn}_参考.wav"),
            os.path.join(self.ref_dir, f"{persona_cn}_参考.mp3"),
            os.path.join(self.ref_dir, f"{persona}_ref.wav"),
            os.path.join(self.ref_dir, f"{persona}_ref.mp3"),
        ]
        
        ref_audio = None
        for path in possible_paths:
            if os.path.exists(path):
                ref_audio = path
                break
        
        if not ref_audio:
            print(f"⚠️ 参考音色 [{persona_cn}] 不存在，回退至说书人")
            ref_audio = os.path.join(self.ref_dir, "旁白_参考.wav")
            # 兜底兜底
            if not os.path.exists(ref_audio):
                ref_audio = os.path.join(self.ref_dir, "narrator_ref.mp3")
        
        # 无论如何，最终交给 model 的路径一定是来自 temp 且具备中文名
        processed_ref = self._prepare_reference(ref_audio, persona)
        print(f"👥 模式：声音克隆 | 物理参考源 (temp)：{os.path.basename(processed_ref)}")
        
        return self.model.generate_voice_clone(
            text=text, 
            language=language, 
            ref_audio=processed_ref, 
            x_vector_only_mode=True
        )
