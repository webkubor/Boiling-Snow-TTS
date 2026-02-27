import soundfile as sf
from ..utils import generate_output_path, get_persona_cn

class PodcastMode:
    """【模块 4：播客专栏】支持双人对谈逻辑"""
    def __init__(self, engine, processor, cloner):
        self.engine = engine
        self.processor = processor
        self.cloner = cloner

    def run(self, config):
        # 如果配置里有 lines，走对谈逻辑
        if "lines" in config and isinstance(config["lines"], list):
            print(f"🎙️ 进入【播客对谈模式】，专栏：{config.get('title')}")
            segments = []
            for i, line in enumerate(config["lines"]):
                persona = line.get("persona", "yue_qizhou")
                text = line.get("text")
                instruct = f"{line.get('tone','')}，{line.get('emotion','')}".strip("，")
                print(f"\n🎧 正在生成播客片段 {i+1} ({get_persona_cn(persona)})")
                
                wavs, sr = self.cloner.run(persona, text, config.get("language","Chinese"), instruct)
                
                # 播客专用导出：保留分轨
                temp_path = generate_output_path(config, self.engine.base_dir, suffix=f"_seg{i+1}")
                sf.write(temp_path, wavs[0], sr)
                
                # 播客特定后期：不加长留白（缝合时再加），但要标准化和去噪
                seg = self.processor.apply_post_tuning(temp_path, mode="podcast", add_padding=False)
                if seg: segments.append(seg)
            
            # 缝合成完整播客场景
            final_path = generate_output_path(config, self.engine.base_dir)
            self.processor.merge_scene(segments, final_path, gap_ms=1000) # 播客语速稍缓，间隔 1s
            return None, 0, final_path
        
        # 否则走原有的单人独白逻辑
        else:
            print(f"🎙️ 进入【播客独白模式】，专栏：{config.get('title')}")
            persona = "yue_qizhou"
            text = config.get("text")
            lang = config.get("language", "Chinese")
            instruct = f"{config.get('tone','')}，{config.get('emotion','')}".strip("，")
            wavs, sr = self.cloner.run(persona, text, lang, instruct)
            return wavs, sr, None
