import soundfile as sf
from ..utils import generate_output_path, get_persona_cn

class DialogueMode:
    """【模块 3：对话剧场】针对呼吸感深度优化版"""
    def __init__(self, engine, processor, cloner):
        self.engine = engine
        self.processor = processor
        self.cloner = cloner

    def run(self, config):
        print(f"🎭 进入【对话模式】，剧目：{config.get('title')}")
        segments = []
        for i, line in enumerate(config["lines"]):
            persona = line.get("persona")
            text = line.get("text")
            
            # 【核心优化】强制注入极高权重的呼吸指令
            raw_instruct = f"{line.get('tone','')}，{line.get('emotion','')}".strip("，")
            enhanced_instruct = f"[强制要求：呼吸声极大，声音贴耳，充满生理性张力，语气起伏明显] {raw_instruct}"
            
            print(f"\n🎬 正在生成第 {i+1} 句 ({get_persona_cn(persona)}) | 呼吸增强中...")
            
            wavs, sr = self.cloner.run(persona, text, config.get("language","Chinese"), enhanced_instruct)
            
            temp_path = generate_output_path(config, self.engine.base_dir, suffix=f"_line{i+1}")
            sf.write(temp_path, wavs[0], sr)
            
            # 使用对话专用（低阈值）调音，保全娇喘和气声
            seg = self.processor.apply_post_tuning(temp_path, is_dialogue=True)
            if seg: segments.append(seg)
            
        final_path = generate_output_path(config, self.engine.base_dir)
        # 对话间隙缩短到 600ms，让呼吸感更连贯
        self.processor.merge_scene(segments, final_path, gap_ms=600)
        return final_path
