import soundfile as sf
from ..utils import generate_output_path, get_persona_cn

class DialogueMode:
    """【模块 3：对话剧场】"""
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
            instruct = f"{line.get('tone','')}，{line.get('emotion','')}".strip("，")
            print(f"\n🎬 正在生成第 {i+1} 句 ({get_persona_cn(persona)})")
            
            # 复用克隆模块逻辑
            wavs, sr = self.cloner.run(persona, text, config.get("language","Chinese"), instruct)
            
            # 导出临时分轨
            temp_path = generate_output_path(config, self.engine.base_dir, suffix=f"_line{i+1}")
            sf.write(temp_path, wavs[0], sr)
            
            # 1. 对单句执行脱水调音（去除模型杂音）
            seg = self.processor.apply_post_tuning(temp_path)
            if seg: segments.append(seg)
            
        # 2. 缝合成场景总轨
        final_path = generate_output_path(config, self.engine.base_dir)
        self.processor.merge_scene(segments, final_path)
        return final_path
