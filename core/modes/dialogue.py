import os
import soundfile as sf
from pydub import AudioSegment
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
        global_emotion_priority = bool(config.get("emotion_priority", False))
        for i, line in enumerate(config["lines"]):
            persona = line.get("persona") or line.get("role")
            text = line.get("text")
            line_emotion_priority = bool(line.get("emotion_priority", global_emotion_priority))
            
            raw_instruct = f"{line.get('tone','')}，{line.get('emotion','')}".strip("，")
            
            # --- 【灵魂注入：动态反应逻辑】 ---
            # 1. 模拟“听话后”的瞬间反应：先有气，后有声
            # 2. 随机注入发声前的预热指令（轻笑、叹息、深吸气）
            import random
            prep_actions = ["轻笑一声", "深深吸一口气", "先发出一声慵懒的鼻音", "先有一声低沉的喘息"]
            action = random.choice(prep_actions)
            
            enhanced_instruct = f"[强制要求：{action}，说话前留有明显的生理性气口，语气起伏要体现出对上一句话的即时反应] {raw_instruct}"
            
            print(f"\n🎬 正在生成第 {i+1} 句 ({get_persona_cn(persona)}) | 反应预热：{action}...")
            
            wavs, sr = self.cloner.run(
                persona,
                text,
                config.get("language","Chinese"),
                enhanced_instruct,
                emotion_priority=line_emotion_priority,
                allow_ref_fallback=False
            )
            
            temp_path = generate_output_path(config, self.engine.base_dir, suffix=f"_line{i+1}")
            sf.write(temp_path, wavs[0], sr)
            line_paths.append(temp_path)
            
            # 对话模式下，稍微保留一点点句首的静音/气声
            seg = self.processor.apply_post_tuning(temp_path, is_dialogue=True)
            
            # --- 【动态间隙控制】 ---
            # 对话不是平接的，需要 400-800ms 的真实反应间隙
            reaction_gap = AudioSegment.silent(duration=random.randint(400, 800))
            if seg: segments.append(reaction_gap + seg)
            
        final_path = generate_output_path(config, self.engine.base_dir)
        # 间隙已在 segments 中处理，merge_scene 仅负责最终混合
        self.processor.merge_scene(segments, final_path, gap_ms=0) 
        
        # --- 【新增】清理分轨文件，只留最后合成版本 ---
        for path in line_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except: pass
        print(f"🧹 已清理 {len(line_paths)} 个分轨临时文件。")
        
        return final_path
