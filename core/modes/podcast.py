class PodcastMode:
    """【模块 4：播客专栏】"""
    def __init__(self, engine, processor, cloner):
        self.engine = engine
        self.processor = processor
        self.cloner = cloner

    def run(self, config):
        print(f"🎙️ 进入【播客模式】，专栏：{config.get('title')}")
        # 强制锁定身份
        persona = "yue_qizhou"
        text = config.get("text")
        lang = config.get("language", "Chinese")
        instruct = f"{config.get('tone','')}，{config.get('emotion','')}".strip("，")
        
        # 核心逻辑：调用克隆引擎，但使用播客特定的后期调音
        return self.cloner.run(persona, text, lang, instruct)
