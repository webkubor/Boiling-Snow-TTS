from .engine import TTSBaseEngine

class VoiceDesigner(TTSBaseEngine):
    """【分支功能：音色设计】 严格基于文字描述凭空创造声音"""
    
    def __init__(self, model_size="1.7B"):
        super().__init__("VoiceDesign", model_size)

    def process(self, text, language, instruct):
        print(f"🎨 模式：音色设计 | 指令集：{instruct}")
        return self.model.generate_voice_design(
            text=text, 
            language=language, 
            instruct=instruct
        )
