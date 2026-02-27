import soundfile as sf
from ..utils import generate_output_path, get_persona_cn

class PodcastMode:
    """【模块 4：播客专栏】支持双人对谈与灵活身份逻辑"""
    def __init__(self, engine, processor, cloner):
        self.engine = engine
        self.processor = processor
        self.cloner = cloner

    def run(self, config):
        # 1. 对谈模式逻辑
        if "lines" in config and isinstance(config["lines"], list):
            print(f"🎙️ 进入【播客对谈模式】，专栏：{config.get('title')}")
            segments = []
            for i, line in enumerate(config["lines"]):
                persona = line.get("persona", "yue_qizhou")
                text = line.get("text")
                instruct = f"{line.get('tone','')}，{line.get('emotion','')}".strip("，")
                print(f"\n🎧 正在生成播客片段 {i+1} ({get_persona_cn(persona)})")
                
                wavs, sr = self.cloner.run(persona, text, config.get("language","Chinese"), instruct)
                
                temp_path = generate_output_path(config, self.engine.base_dir, suffix=f"_seg{i+1}")
                sf.write(temp_path, wavs[0], sr)
                
                seg = self.processor.apply_post_tuning(temp_path, mode="podcast", add_padding=False)
                if seg: segments.append(seg)
            
            final_path = generate_output_path(config, self.engine.base_dir)
            self.processor.merge_scene(segments, final_path, gap_ms=1000)
            return None, 0, final_path
        
        # 2. 单人模式逻辑
        else:
            print(f"🎙️ 进入【播客单人模式】，专栏：{config.get('title')}")
            persona = config.get("persona", "yue_qizhou")
            text = config.get("text")
            lang = config.get("language", "Chinese")
            instruct = f"{config.get('tone','')}，{config.get('emotion','')}".strip("，")
            
            wavs, sr = self.cloner.run(persona, text, lang, instruct)
            return wavs, sr, None
