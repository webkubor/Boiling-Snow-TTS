import os
import sys
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
        temp_name = f"当前参考_{persona_cn}.mp3"
        temp_path = os.path.join(self.temp_dir, temp_name)
        
        try:
            audio = AudioSegment.from_file(audio_path)
            duration_sec = len(audio) / 1000.0
            
            if duration_sec > max_sec:
                print(f"✂️ AI 自动剪辑：参考音频过长 ({duration_sec:.1f}s)，正在截取前 {max_sec}s...")
                audio = audio[:max_sec * 1000]
            
            audio.export(temp_path, format="mp3")
            return temp_path
        except Exception as e:
            print(f"⚠️ 样音流转失败: {e}，回退使用原始路径")
            return audio_path

    def process(self, text, persona, language, instruct):
        persona_cn = get_persona_cn(persona)
        
        # 寻找参考音频
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
        
        # 【核心引导：如果参考音频不存在，中断并引导用户】
        if not ref_audio:
            print("\n" + "="*60)
            print(f"❌ 错误：找不到角色【{persona_cn}】的参考音频底稿！")
            print("="*60)
            print(f"💡 解决方法：")
            print(f"1. 请准备一段该角色的原始录音（任意时长，AI会自动剪辑）。")
            print(f"2. 将音频文件放入目录：assets/reference_audio/")
            print(f"3. 命名文件为：{persona_cn}_参考.wav (或 .mp3)")
            print("="*60 + "\n")
            sys.exit(1) # 强行中断任务，等待用户补齐素材
        
        processed_ref = self._prepare_reference(ref_audio, persona)
        print(f"👥 模式：声音克隆 | 物理参考源 (temp)：{os.path.basename(processed_ref)}")
        
        return self.model.generate_voice_clone(
            text=text, 
            language=language, 
            ref_audio=processed_ref, 
            x_vector_only_mode=True
        )
