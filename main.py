import os
import sys
import soundfile as sf
from core.engine import TTSBaseEngine
from core.processor import AudioProcessor
from core.utils import load_config, generate_output_path, get_persona_cn, log_generation_metadata, post_process_audio
from core.modes.cloner import CloneMode
from core.modes.designer import DesignMode
from core.modes.dialogue import DialogueMode
from core.modes.podcast import PodcastMode

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 1. 配置加载路由
    config_name = "movie_config.json"
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        config_name = "podcast_config.json" if arg == "podcast" else (arg if arg.endswith(".json") else config_name)
    
    cfg = load_config(os.path.join(BASE_DIR, "configs", config_name))
    
    # 2. 初始化原子化组件
    engine = TTSBaseEngine(cfg.get("model_type", "Base"), cfg.get("model_size", "1.7B"))
    processor = AudioProcessor(BASE_DIR)
    
    # 3. 实例化功能模块
    cloner = CloneMode(engine, processor)
    designer = DesignMode(engine, processor)
    dialogue = DialogueMode(engine, processor, cloner)
    podcast = PodcastMode(engine, processor, cloner)
    
    # 4. 模式派发
    mode_type = cfg.get("model_type", "Base")
    content_type = cfg.get("content_type", "movie")
    is_dial = "lines" in cfg and isinstance(cfg["lines"], list)
    
    if content_type == "podcast":
        # 播客模式 (支持独白和对谈)
        wavs, sr, final_path = podcast.run(cfg)
        if wavs: # 独白模式
            final_path = generate_output_path(cfg, BASE_DIR)
            sf.write(final_path, wavs[0], sr)
            processor.apply_post_tuning(final_path, mode="podcast")
        # 对谈模式下，PodcastMode 已处理完 final_path
    elif is_dial:
        # 微电影对话模式
        final_path = dialogue.run(cfg)
    elif mode_type == "VoiceDesign":
        # 设计模式
        instruct = f"{cfg.get('tone','')}, {cfg.get('emotion','')}".strip(", ")
        wavs, sr = designer.run(cfg["text"], cfg.get("language","Chinese"), instruct)
        final_path = generate_output_path(cfg, BASE_DIR)
        sf.write(final_path, wavs[0], sr)
        ref_name = f"{get_persona_cn(cfg.get('persona'))}_参考.wav"
        sf.write(os.path.join(BASE_DIR, "assets/reference_audio", ref_name), wavs[0], sr)
        processor.apply_post_tuning(final_path, mode="movie")
    else:
        # 基础克隆模式
        instruct = f"{cfg.get('tone','')}, {cfg.get('emotion','')}".strip(", ")
        wavs, sr = cloner.run(cfg.get("persona"), cfg["text"], cfg.get("language","Chinese"), instruct)
        final_path = generate_output_path(cfg, BASE_DIR)
        sf.write(final_path, wavs[0], sr)
        processor.apply_post_tuning(final_path, mode="movie")

    print(f"\n✨ 生成成功！任务已闭环。\n📂 最终成品：{final_path}")
    log_generation_metadata(cfg, final_path, BASE_DIR)

if __name__ == "__main__":
    main()
