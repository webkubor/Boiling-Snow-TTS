import os
import sys
from ..utils import get_persona_cn

class CloneMode:
    """【模块 1：单人克隆】"""
    def __init__(self, engine, processor):
        self.engine = engine
        self.processor = processor
        self.ref_dir = os.path.join(engine.base_dir, "assets/reference_audio")

    def run(self, persona, text, lang, instruct):
        p_cn = get_persona_cn(persona)
        # 搜寻底稿
        ref_audio = None
        for name in [f"{p_cn}_参考", f"{persona}_ref"]:
            for ext in [".wav", ".mp3", ".m4a"]:
                path = os.path.join(self.ref_dir, name + ext)
                if os.path.exists(path):
                    ref_audio = path; break
            if ref_audio: break
        
        if not ref_audio:
            print(f"
❌ 错误：找不到角色【{p_cn}】的参考音频！"); sys.exit(1)
            
        # 1. 独立调用样音提取
        seed = self.processor.extract_voice_seed(ref_audio, p_cn)
        print(f"👥 模式：声音克隆 | 物理参考源：{os.path.basename(seed)}")
        
        # 2. 调用模型生成
        wavs, sr = self.engine.model.generate_voice_clone(
            text=text, language=lang, ref_audio=seed, x_vector_only_mode=True
        )
        return wavs, sr
