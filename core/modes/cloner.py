import os
import sys
import torch
from ..utils import get_persona_cn

class CloneMode:
    """【模块 1：单人克隆】 深度重构：支持指令克隆，开启 1.7B 演技模式"""
    def __init__(self, engine, processor):
        self.engine = engine
        self.processor = processor
        self.ref_dir = os.path.join(engine.base_dir, "assets/reference_audio")
        self.seed_dir = os.path.join(engine.base_dir, "assets/designed_seeds")

    def run(self, persona, text, lang, instruct):
        p_cn = get_persona_cn(persona)
        
        possible_exts = [".wav", ".mp3", ".m4a"]
        ref_audio = None
        for search_dir in [self.ref_dir, self.seed_dir]:
            for name in [f"{p_cn}_参考", f"{persona}_ref"]:
                for ext in possible_exts:
                    path = os.path.join(search_dir, name + ext)
                    if os.path.exists(path):
                        ref_audio = path; break
                if ref_audio: break
            if ref_audio: break
        
        if not ref_audio:
            print(f"\n❌ 错误：找不到角色【{p_cn}】的参考音频！"); sys.exit(1)
            
        seed = self.processor.extract_voice_seed(ref_audio, p_cn)
        
        # --- 【关键重构：通过 VoiceDesign 引擎实现指令级克隆】 ---
        # 1. 如果有 instruct，我们尝试利用 VoiceDesign 的强大情绪控制力
        # 但 VoiceDesign 无法直接接受 ref_audio。
        # 2. 正确做法：使用 Base 1.7B 模型，并确保指令 Token 维度与输入文本一致。
        
        instruct_text = f"<|im_start|>user\n{instruct}<|im_end|>\n"
        input_objs = self.engine.processor(text=instruct_text, return_tensors="pt", padding=True)
        instruct_ids = input_objs["input_ids"].to(self.engine.device) # 默认 [1, Seq]
        
        print(f"👥 模式：指令克隆 | 角色：{p_cn} | 演技负载：{instruct[:30]}...")
        
        # --- 【修复音色漂移：固定随机种子】 ---
        torch.manual_seed(42)
        if torch.cuda.is_available(): torch.cuda.manual_seed_all(42)
        
        # 在 generate_voice_clone 中，instruct_ids 应该以 List[Tensor] 传入且 Tensor 维度为 [1, Seq]
        # 底层逻辑会将其与 input_ids 合并。刚才报错是因为 Batch 维度冲突。
        
        wavs, sr = self.engine.wrapped_model.generate_voice_clone(
            text=text, 
            language=lang, 
            ref_audio=seed, 
            x_vector_only_mode=True,
            instruct_ids=[instruct_ids] # 包装在列表中
        )
        return wavs, sr
