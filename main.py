import os
import sys
import soundfile as sf
from core.engine import TTSBaseEngine
from core.processor import AudioProcessor
from core.utils import (
    load_config,
    generate_output_path,
    get_persona_cn,
    log_generation_metadata,
    resolve_config_path,
    validate_runtime_config,
)
from core.modes.cloner import CloneMode
from core.modes.designer import DesignMode
from core.modes.dialogue import DialogueMode

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    config_arg = sys.argv[1].lower() if len(sys.argv) > 1 else "single"
    try:
        cfg_path, config_ref = resolve_config_path(config_arg)
    except ValueError as e:
        print(f"❌ 配置参数错误：{e}")
        sys.exit(1)

    print(f"📖 正在加载配置：{config_ref}")
    cfg = load_config(cfg_path)
    validate_runtime_config(cfg, config_ref)
    
    # 2. 初始化环境
    m_size = cfg.get("model_size", "1.7B")
    mode_type = cfg.get("model_type", "Base")
    engine = TTSBaseEngine(mode_type, m_size)
    processor = AudioProcessor(BASE_DIR)
    
    cloner = CloneMode(engine, processor)
    designer = DesignMode(engine, processor)
    dialogue = DialogueMode(engine, processor, cloner)
    
    # 智能识别任务类型
    task_type = cfg.get("type", "single") 
    is_dial = task_type == "dialogue" or ("lines" in cfg and isinstance(cfg["lines"], list))
    
    # 3. 模式分发
    if mode_type == "VoiceDesign":
        # ... (保持原逻辑)
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

    else:
        # 默认走 CloneMode (单人任务)
        instruct = f"{cfg.get('tone','')}, {cfg.get('emotion','')}".strip(", ")
        wavs, sr = cloner.run(cfg.get("persona"), cfg.get("text", ""), cfg.get("language","Chinese"), instruct)
        final_path = generate_output_path(cfg, BASE_DIR)
        sf.write(final_path, wavs[0], sr)
        processor.apply_post_tuning(final_path)

    print(f"\n✨ 生成成功！任务已闭环。\n📂 最终成品：{final_path}")
    log_generation_metadata(cfg, final_path, BASE_DIR)

if __name__ == "__main__":
    main()
