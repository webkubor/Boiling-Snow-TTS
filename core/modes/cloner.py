import os
import sys
import torch
from ..utils import get_persona_cn

class CloneMode:
    """【模块 1：单人克隆】 深度重构：支持指令克隆，开启 1.7B 演技模式"""
    def __init__(self, engine, processor):
        self.engine = engine
        self.processor = processor
        self.seed_dir = os.path.join(engine.base_dir, "assets/output_audio/designed_seeds")

    def run(self, persona, text, lang, instruct, emotion_priority=False):
        from ..utils import get_persona_cn
        p_cn = get_persona_cn(persona)

        # --- 强力约束：只准在 temp 里找黄金样音 ---
        ref_audio = os.path.join(self.engine.base_dir, "assets/temp", f"当前参考_{p_cn}.wav")

        if not os.path.exists(ref_audio):
            print(f"\n❌ 错误：找不到角色【{p_cn}】的参考音频资产！")
            print(f"👉 请确保 {ref_audio} 存在（即已完成 1.5s 避障处理的黄金 10s 样音）。")
            sys.exit(1)

        seed = ref_audio  # 直接使用 temp 里的黄金样音

        # --- 合并指令：基础音色描述 + 实时情绪控制 ---
        from ..utils import get_persona_map
        persona_map = get_persona_map()
        persona_data = persona_map.get(persona, {})
        base_instruct = ""
        if isinstance(persona_data, dict) and "instruction" in persona_data:
            base_instruct = persona_data["instruction"]

        if emotion_priority:
            final_instruct = (instruct or "").strip() or base_instruct
        else:
            final_instruct = f"{base_instruct} {instruct}".strip()
        instruct_text = f"<|im_start|>user\n{final_instruct}<|im_end|>\n"
        input_objs = self.engine.processor(text=instruct_text, return_tensors="pt", padding=True)
        instruct_ids = input_objs["input_ids"].to(self.engine.device) 

        priority_tag = "情绪优先" if emotion_priority else "人设优先"
        print(f"👥 模式：指令克隆({priority_tag}) | 角色：{p_cn} | 演技负载：{final_instruct[:50]}...")

        torch.manual_seed(42)
        if torch.cuda.is_available(): torch.cuda.manual_seed_all(42)

        # --- 稳住音色与台词完整性 ---
        wavs, sr = self.engine.wrapped_model.generate_voice_clone(
            text=text, 
            language=lang, 
            ref_audio=seed, 
            x_vector_only_mode=True,
            instruct_ids=[instruct_ids],
            do_sample=True,
            temperature=0.7,  # 稍微压低，稳住原声底色
            top_p=0.9,       # 过滤掉不稳定的采样分支
            top_k=50
        )
        return wavs, sr
