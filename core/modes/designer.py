class DesignMode:
    """【模块 2：音色设计】"""
    def __init__(self, engine, processor):
        self.engine = engine
        self.processor = processor

    def run(self, text, lang, instruct):
        print(f"🎨 模式：音色设计 | 指令集：{instruct}")
        return self.engine.model.generate_voice_design(
            text=text, language=lang, instruct=instruct
        )
