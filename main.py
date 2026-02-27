import os
import shutil
import soundfile as sf
import sys
from core.cloner import VoiceCloner
from core.designer import VoiceDesigner
from core.utils import load_config, generate_output_path, get_persona_cn, log_generation_metadata, post_process_audio

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # --- 智能配置选择逻辑 ---
    # 默认使用 movie_config.json，支持通过命令行参数切换：python main.py podcast
    config_name = "movie_config.json"
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "podcast":
            config_name = "podcast_config.json"
        elif arg.endswith(".json"):
            config_name = arg
            
    CONFIG_PATH = os.path.join(BASE_DIR, "configs", config_name)
    REF_DIR = os.path.join(BASE_DIR, "assets/reference_audio")
    
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ 错误：找不到配置文件 {CONFIG_PATH}")
        sys.exit(1)
        
    print(f"📖 正在加载配置：{config_name}")
    cfg = load_config(CONFIG_PATH)
    m_type = cfg.get("model_type", "Base")
    m_size = cfg.get("model_size", "1.7B")
    persona_en = cfg.get("persona", "unknown")
    persona_cn = get_persona_cn(persona_en)
    content_type = cfg.get("content_type", "movie")
    
    # --- 核心路由派发 ---
    if m_type == "VoiceDesign":
        # 进入【设计分支】
        studio = VoiceDesigner(model_size=m_size)
        instruct = f"{cfg.get('tone', '')}，{cfg.get('emotion', '')}".strip("，")
        wavs, sr = studio.process(cfg["text"], cfg.get("language", "Chinese"), instruct)
        
        # 【设计入库逻辑】
        ref_save_name = f"{persona_cn}_参考.wav"
        sf.write(os.path.join(REF_DIR, ref_save_name), wavs[0], sr)
        print(f"✅ 角色音色已自动入库参考目录：{ref_save_name}")
        
    else:
        # 进入【克隆分支】
        studio = VoiceCloner(model_size=m_size)
        instruct = f"{cfg.get('tone', '')}，{cfg.get('emotion', '')}".strip("，")
        wavs, sr = studio.process(cfg["text"], persona_en, cfg.get("language", "Chinese"), instruct)

    # --- 统一导出成品 ---
    output_path = generate_output_path(cfg, BASE_DIR)
    sf.write(output_path, wavs[0], sr)
    
    # 执行音频后期调音
    post_process_audio(output_path, content_type=content_type)
    
    print(f"\n✨ 生成完成！成品已存至：\n📂 {output_path}")
    
    # 记录台词元数据
    log_generation_metadata(cfg, output_path, BASE_DIR)

if __name__ == "__main__":
    main()
