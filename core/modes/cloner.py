import os
import sys
from ..utils import get_persona_cn

class CloneMode:
    """【模块 1：单人克隆】 支持双库搜寻（资产库+样音库）"""
    def __init__(self, engine, processor):
        self.engine = engine
        self.processor = processor
        self.ref_dir = os.path.join(engine.base_dir, "assets/reference_audio")
        self.seed_dir = os.path.join(engine.base_dir, "assets/designed_seeds")

    def run(self, persona, text, lang, instruct):
        p_cn = get_persona_cn(persona)
        
        # --- 策略：双库搜寻 ---
        possible_exts = [".wav", ".mp3", ".m4a"]
        ref_audio = None
        
        # 1. 先搜寻“资产库”（用户原声）
        # 2. 再搜寻“样音库”（AI捏人种子）
        for search_dir in [self.ref_dir, self.seed_dir]:
            for name in [f"{p_cn}_参考", f"{persona}_ref"]:
                for ext in possible_exts:
                    path = os.path.join(search_dir, name + ext)
                    if os.path.exists(path):
                        ref_audio = path; break
                if ref_audio: break
            if ref_audio: break
        
        if not ref_audio:
            print(f"\n❌ 错误：找不到角色【{p_cn}】的参考音频！\n💡 请将原始音频放入 assets/reference_audio/ 目录下并命名为 [{p_cn}_参考.wav]")
            sys.exit(1)
            
        seed = self.processor.extract_voice_seed(ref_audio, p_cn)
        print(f"👥 模式：声音克隆 | 物理参考源：{os.path.basename(seed)}")
        
        wavs, sr = self.engine.model.generate_voice_clone(
            text=text, language=lang, ref_audio=seed, x_vector_only_mode=True
        )
        return wavs, sr
