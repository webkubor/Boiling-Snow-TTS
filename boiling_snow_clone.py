import os
import soundfile as sf
from core.cloner import VoiceCloner
from core.designer import VoiceDesigner
from core.utils import load_config, generate_output_path

def main():
    # --- 初始化环境 ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CONFIG_PATH = os.path.join(BASE_DIR, "configs/config.json")
    
    # 加载配置
    cfg = load_config(CONFIG_PATH)
    m_type = cfg.get("model_type", "Base")
    m_size = cfg.get("model_size", "1.7B")
    
    # --- 核心路由派发 ---
    if m_type == "VoiceDesign":
        # 进入【设计分支】
        studio = VoiceDesigner(model_size=m_size)
        instruct = f"{cfg.get('tone', '')}，{cfg.get('emotion', '')}".strip("，")
        wavs, sr = studio.process(cfg["text"], cfg.get("language", "Chinese"), instruct)
    else:
        # 进入【克隆分支】
        studio = VoiceCloner(model_size=m_size)
        instruct = f"{cfg.get('tone', '')}，{cfg.get('emotion', '')}".strip("，")
        wavs, sr = studio.process(cfg["text"], cfg.get("persona", "narrator"), cfg.get("language", "Chinese"), instruct)

    # --- 统一导出成品 ---
    output_path = generate_output_path(cfg, BASE_DIR)
    sf.write(output_path, wavs[0], sr)
    print(f"\n✨ 生成完成！江湖回响已存至：\n📂 {output_path}")

if __name__ == "__main__":
    main()
