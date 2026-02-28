import os
import sys
import torch
from ..utils import get_persona_cn

class CloneMode:
    """【模块 1：单人克隆】 深度重构：支持指令克隆，开启 1.7B 演技模式"""
    def __init__(self, engine, processor):
        self.engine = engine
        self.processor = processor
        self.seed_dir = os.path.join(engine.base_dir, "assets/designed_seeds")

    def run(self, persona, text, lang, instruct):
        from ..utils import get_persona_map, get_persona_cn, load_config, resolve_persona_ref_audio
        persona_map = get_persona_map()
        persona_data = persona_map.get(persona, {})
        p_cn = get_persona_cn(persona)
        
        # --- 核心改进：解析资产路径 (优先设计配方，其次样音) ---
        ref_audio = None
        base_instruct = ""
        
        if isinstance(persona_data, dict):
            # 1. 优先尝试加载音色设计 JSON
            design_rel_path = persona_data.get("design")
            if design_rel_path:
                design_path = os.path.join(self.engine.base_dir, design_rel_path)
                if os.path.exists(design_path):
                    design_info = load_config(design_path)
                    formula = design_info.get("instruction_formula", {})
                    base_instruct = formula.get("full_prompt", "")
                    # 查找种子音频
                    seed_name = design_info.get("reference_seed_audio", f"{p_cn}_参考.wav")
                    ref_audio = os.path.join(self.seed_dir, seed_name)
                    if not os.path.exists(ref_audio): ref_audio = None

            # 2. 如果没有设计配方或找不到种子音，尝试使用 ref 字段
            if not ref_audio and "ref" in persona_data:
                try:
                    ref_audio = resolve_persona_ref_audio(self.engine.base_dir, persona, persona_data)
                except ValueError as e:
                    print(f"\n❌ 错误：{e}")
                    sys.exit(1)
        
        if not ref_audio:
            print(f"\n❌ 错误：找不到角色【{p_cn}】的参考音频。请按 <角色名>_参考.<ext> 放在 assets/reference_audio/"); sys.exit(1)
            
        seed = self.processor.extract_voice_seed(ref_audio, p_cn)
        
        # --- 合并指令：基础音色描述 + 实时情绪控制 ---
        if isinstance(persona_data, dict) and "instruction" in persona_data:
            base_instruct = persona_data["instruction"]
            
        final_instruct = f"{base_instruct} {instruct}".strip()
        instruct_text = f"<|im_start|>user\n{final_instruct}<|im_end|>\n"
        input_objs = self.engine.processor(text=instruct_text, return_tensors="pt", padding=True)
        instruct_ids = input_objs["input_ids"].to(self.engine.device) 
        
        print(f"👥 模式：指令克隆 | 角色：{p_cn} | 演技负载：{final_instruct[:50]}...")
        
        torch.manual_seed(42)
        if torch.cuda.is_available(): torch.cuda.manual_seed_all(42)
        
        wavs, sr = self.engine.wrapped_model.generate_voice_clone(
            text=text, 
            language=lang, 
            ref_audio=seed, 
            x_vector_only_mode=True,
            instruct_ids=[instruct_ids] 
        )
        return wavs, sr
