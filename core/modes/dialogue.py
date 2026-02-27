import os
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
        line_paths = []
        for i, line in enumerate(config["lines"]):
            persona = line.get("persona")
            text = line.get("text")
            
            raw_instruct = f"{line.get('tone','')}，{line.get('emotion','')}".strip("，")
            enhanced_instruct = f"[强制要求：呼吸声极大，声音贴耳，充满生理性张力，语气起伏明显] {raw_instruct}"
            
            print(f"\n🎬 正在生成第 {i+1} 句 ({get_persona_cn(persona)}) | 呼吸增强中...")
            
            wavs, sr = self.cloner.run(persona, text, config.get("language","Chinese"), enhanced_instruct)
            
            temp_path = generate_output_path(config, self.engine.base_dir, suffix=f"_line{i+1}")
            sf.write(temp_path, wavs[0], sr)
            line_paths.append(temp_path)
            
            seg = self.processor.apply_post_tuning(temp_path, is_dialogue=True)
            if seg: segments.append(seg)
            
        final_path = generate_output_path(config, self.engine.base_dir)
        self.processor.merge_scene(segments, final_path, gap_ms=600)
        
        # --- 【新增】清理分轨文件，只留最后合成版本 ---
        for path in line_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except: pass
        print(f"🧹 已清理 {len(line_paths)} 个分轨临时文件。")
        
        return final_path
