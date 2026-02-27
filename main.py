import os
import shutil
import soundfile as sf
from core.cloner import VoiceCloner
from core.designer import VoiceDesigner
from core.utils import load_config, generate_output_path, get_persona_cn, log_generation_metadata

def main():
    # --- 初始化环境 ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(BASE_DIR, "configs/config.json")
    REF_DIR = os.path.join(BASE_DIR, "assets/reference_audio")
    
    # 加载配置
    cfg = load_config(CONFIG_PATH)
    m_type = cfg.get("model_type", "Base")
    m_size = cfg.get("model_size", "1.7B")
    persona_en = cfg.get("persona", "unknown")
    persona_cn = get_persona_cn(persona_en)
    
    # --- 核心路由派发 ---
    if m_type == "VoiceDesign":
        # 进入【设计分支】
        studio = VoiceDesigner(model_size=m_size)
        instruct = f"{cfg.get('tone', '')}，{cfg.get('emotion', '')}".strip("，")
        wavs, sr = studio.process(cfg["text"], cfg.get("language", "Chinese"), instruct)
        
        # 【设计入库逻辑】统一使用中文名：角色名_参考.wav
        ref_save_name = f"{persona_cn}_参考.wav"
        ref_save_path = os.path.join(REF_DIR, ref_save_name)
        sf.write(ref_save_path, wavs[0], sr)
        print(f"✅ 角色音色已自动入库参考目录：{ref_save_name}")
        
    else:
        # 进入【克隆分支】
        studio = VoiceCloner(model_size=m_size)
        instruct = f"{cfg.get('tone', '')}，{cfg.get('emotion', '')}".strip("，")
        wavs, sr = studio.process(cfg["text"], persona_en, cfg.get("language", "Chinese"), instruct)

    # --- 统一导出成品 ---
    output_path = generate_output_path(cfg, BASE_DIR)
    sf.write(output_path, wavs[0], sr)
    print(f"\n✨ 生成完成！江湖回响已存至：\n📂 {output_path}")
    
    # --- 【新增】记录台词与音频的对应关系 ---
    log_generation_metadata(cfg, output_path, BASE_DIR)

if __name__ == "__main__":
    main()
