import os
import shutil
import soundfile as sf
from core.cloner import VoiceCloner
from core.designer import VoiceDesigner
from core.utils import load_config, generate_output_path, get_persona_cn, log_generation_metadata, post_process_audio

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(BASE_DIR, "configs/config.json")
    REF_DIR = os.path.join(BASE_DIR, "assets/reference_audio")
    
    cfg = load_config(CONFIG_PATH)
    m_type = cfg.get("model_type", "Base")
    m_size = cfg.get("model_size", "1.7B")
    persona_en = cfg.get("persona", "unknown")
    persona_cn = get_persona_cn(persona_en)
    content_type = cfg.get("content_type", "movie")
    
    if m_type == "VoiceDesign":
        studio = VoiceDesigner(model_size=m_size)
        instruct = f"{cfg.get('tone', '')}，{cfg.get('emotion', '')}".strip("，")
        wavs, sr = studio.process(cfg["text"], cfg.get("language", "Chinese"), instruct)
        ref_save_name = f"{persona_cn}_参考.wav"
        sf.write(os.path.join(REF_DIR, ref_save_name), wavs[0], sr)
    else:
        studio = VoiceCloner(model_size=m_size)
        instruct = f"{cfg.get('tone', '')}，{cfg.get('emotion', '')}".strip("，")
        wavs, sr = studio.process(cfg["text"], persona_en, cfg.get("language", "Chinese"), instruct)

    output_path = generate_output_path(cfg, BASE_DIR)
    sf.write(output_path, wavs[0], sr)
    
    # --- 【新增】执行音频后期调音 ---
    post_process_audio(output_path, content_type=content_type)
    
    print(f"\n✨ 生成完成！江湖回响已存至：\n📂 {output_path}")
    log_generation_metadata(cfg, output_path, BASE_DIR)

if __name__ == "__main__":
    main()
