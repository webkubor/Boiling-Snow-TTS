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
    
    # 1. 配置加载路由
    config_name = "movie_config.json"
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        config_name = "podcast_config.json" if arg == "podcast" else (arg if arg.endswith(".json") else config_name)
    
    cfg = load_config(os.path.join(BASE_DIR, "configs", config_name))
    
    # 2. 初始化引擎与处理器
    m_size = cfg.get("model_size", "1.7B")
    engine = TTSBaseEngine(cfg.get("model_type", "Base"), m_size)
    processor = AudioProcessor(BASE_DIR)
    
    # 3. 实例化功能模块
    cloner = CloneMode(engine, processor)
    designer = DesignMode(engine, processor)
    dialogue = DialogueMode(engine, processor, cloner)
    podcast = PodcastMode(engine, processor, cloner)
    
    mode_type = cfg.get("model_type", "Base")
    content_type = cfg.get("content_type", "movie")
    is_dial = "lines" in cfg and isinstance(cfg["lines"], list)
    
    # --- 4. 智能路由派发 ---
    
    if mode_type == "VoiceDesign":
        instruct = f"{cfg.get('tone','')}, {cfg.get('emotion','')}".strip(", ")
        wavs, sr = designer.run(cfg["text"], cfg.get("language","Chinese"), instruct)
        final_path = generate_output_path(cfg, BASE_DIR)
        sf.write(final_path, wavs[0], sr)
        
        # 设计入库
        persona_cn = get_persona_cn(cfg.get('persona'))
        ref_name = f"{persona_cn}_参考.wav"
        ref_path = os.path.join(BASE_DIR, "assets/reference_audio", ref_name)
        sf.write(ref_path, wavs[0], sr)
        processor.extract_voice_seed(ref_path, persona_cn)
        
        # 统一执行原子化调音
        processor.apply_post_tuning(final_path)

    elif is_dial:
        # 对话模式 (其内部已包含分轨处理与总轨缝合)
        final_path = dialogue.run(cfg)

    elif content_type == "podcast":
        wavs, sr, _ = podcast.run(cfg)
        final_path = generate_output_path(cfg, BASE_DIR)
        sf.write(final_path, wavs[0], sr)
        processor.apply_post_tuning(final_path)

    else:
        instruct = f"{cfg.get('tone','')}, {cfg.get('emotion','')}".strip(", ")
        wavs, sr = cloner.run(cfg.get("persona"), cfg["text"], cfg.get("language","Chinese"), instruct)
        final_path = generate_output_path(cfg, BASE_DIR)
        sf.write(final_path, wavs[0], sr)
        processor.apply_post_tuning(final_path)

    print(f"\n✨ 生成成功！任务已闭环。\n📂 最终成品：{final_path}")
    log_generation_metadata(cfg, final_path, BASE_DIR)

if __name__ == "__main__":
    main()
