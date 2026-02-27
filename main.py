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
    mode_type = cfg.get("model_type", "Base")
    m_size = cfg.get("model_size", "1.7B")
    engine = TTSBaseEngine(mode_type, m_size)
    processor = AudioProcessor(BASE_DIR)
    
    # 3. 实例化功能模块
    cloner = CloneMode(engine, processor)
    designer = DesignMode(engine, processor)
    dialogue = DialogueMode(engine, processor, cloner)
    podcast = PodcastMode(engine, processor, cloner)
    
    content_type = cfg.get("content_type", "movie")
    is_dial = "lines" in config_lines if (config_lines := cfg.get("lines")) and isinstance(config_lines, list) else False
    
    # --- 4. 智能路由派发 ---
    
    if mode_type == "VoiceDesign":
        instruct = f"{cfg.get('tone','')}, {cfg.get('emotion','')}".strip(", ")
        wavs, sr = designer.run(cfg["text"], cfg.get("language","Chinese"), instruct)
        final_path = generate_output_path(cfg, BASE_DIR)
        sf.write(final_path, wavs[0], sr)
        
        # --- 【资产隔离修复】捏出来的种子存入专用样音库，不污染原声资产库 ---
        persona_cn = get_persona_cn(cfg.get('persona'))
        ref_name = f"{persona_cn}_参考.wav"
        seed_path = os.path.join(BASE_DIR, "assets/designed_seeds", ref_name)
        sf.write(seed_path, wavs[0], sr)
        
        # 同步脱水入库 temp
        processor.extract_voice_seed(seed_path, persona_cn)
        print(f"✅ 角色音色已同步至【样音库】与 temp 缓存：{persona_cn}")
        
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
            # 对谈模式已由 podcast.run 处理
            final_path = generate_output_path(cfg, BASE_DIR)

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
