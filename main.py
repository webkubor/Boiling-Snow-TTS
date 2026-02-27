import os
import sys
import soundfile as sf
from core.engine import TTSBaseEngine
from core.processor import AudioProcessor
from core.utils import load_config, generate_output_path, get_persona_cn, log_generation_metadata
from core.modes.cloner import CloneMode
from core.modes.designer import DesignMode
from core.modes.dialogue import DialogueMode
from core.modes.podcast import PodcastMode

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # --- 增强版智能路由 ---
    config_name = "movie_config.json"
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "podcast":
            config_name = "podcast_config.json"
        elif arg == "scene": # 【新增】快捷指向场景模板
            config_name = "scene_config.json"
        elif arg.endswith(".json"):
            config_name = arg
    
    cfg_path = os.path.join(BASE_DIR, "configs", config_name)
    if not os.path.exists(cfg_path):
        print(f"❌ 错误：找不到配置文件 {cfg_path}"); sys.exit(1)
    
    print(f"📖 正在加载配置：{config_name}")
    cfg = load_config(cfg_path)
    
    # 2. 初始化环境
    m_size = cfg.get("model_size", "1.7B")
    mode_type = cfg.get("model_type", "Base")
    engine = TTSBaseEngine(mode_type, m_size)
    processor = AudioProcessor(BASE_DIR)
    
    cloner = CloneMode(engine, processor)
    designer = DesignMode(engine, processor)
    dialogue = DialogueMode(engine, processor, cloner)
    podcast = PodcastMode(engine, processor, cloner)
    
    content_type = cfg.get("content_type", "movie")
    is_dial = "lines" in cfg and isinstance(cfg["lines"], list)
    
    # 3. 模式分发
    if mode_type == "VoiceDesign":
        instruct = f"{cfg.get('tone','')}, {cfg.get('emotion','')}".strip(", ")
        wavs, sr = designer.run(cfg.get("text", ""), cfg.get("language","Chinese"), instruct)
        final_path = generate_output_path(cfg, BASE_DIR)
        sf.write(final_path, wavs[0], sr)
        persona_cn = get_persona_cn(cfg.get('persona'))
        seed_path = os.path.join(BASE_DIR, "assets/designed_seeds", f"{persona_cn}_参考.wav")
        sf.write(seed_path, wavs[0], sr)
        processor.extract_voice_seed(seed_path, persona_cn)
        processor.apply_post_tuning(final_path)

    elif is_dial:
        final_path = dialogue.run(cfg)

    elif content_type == "podcast":
        wavs, sr, _ = podcast.run(cfg)
        if wavs:
            final_path = generate_output_path(cfg, BASE_DIR)
            sf.write(final_path, wavs[0], sr)
            processor.apply_post_tuning(final_path)
        else:
            final_path = generate_output_path(cfg, BASE_DIR)

    else:
        instruct = f"{cfg.get('tone','')}, {cfg.get('emotion','')}".strip(", ")
        wavs, sr = cloner.run(cfg.get("persona"), cfg.get("text", ""), cfg.get("language","Chinese"), instruct)
        final_path = generate_output_path(cfg, BASE_DIR)
        sf.write(final_path, wavs[0], sr)
        processor.apply_post_tuning(final_path)

    print(f"\n✨ 生成成功！任务已闭环。\n📂 最终成品：{final_path}")
    log_generation_metadata(cfg, final_path, BASE_DIR)

if __name__ == "__main__":
    main()
