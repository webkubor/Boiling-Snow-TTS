import os
import torch
from qwen_tts import Qwen3TTSModel

class TTSBaseEngine:
    """基础引擎类：处理硬件加速与模型加载"""
    def __init__(self, model_type, model_size):
        # 开启 Mac MPS 兼容性支持
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
        
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_path = os.path.join(self.base_dir, f"models/{model_type}-{model_size}")
        
        if not os.path.exists(self.model_path):
            print(f"⚠️ 路径 {self.model_path} 不存在，尝试默认 Base-0.6B")
            self.model_path = os.path.join(self.base_dir, "models/Base-0.6B")

        self.device, self.dtype = self._detect_device()
        print(f"🚀 正在加载 [{model_type}-{model_size}] 引擎到 {self.device.upper()}...")
        
        try:
            # 加载包装模型
            self.wrapped_model = Qwen3TTSModel.from_pretrained(
                self.model_path,
                device_map=self.device,
                dtype=self.dtype,
                attn_implementation="sdpa"
            )
            # 提取核心组件方便后续直接调用底层 generate
            self.model = self.wrapped_model.model
            self.processor = self.wrapped_model.processor
            
        except Exception as e:
            print(f"⚠️ 硬件加速启动失败，回退到 CPU... ({e})")
            self.wrapped_model = Qwen3TTSModel.from_pretrained(
                self.model_path, 
                device_map="cpu", 
                dtype=torch.float32
            )
            self.model = self.wrapped_model.model
            self.processor = self.wrapped_model.processor

    def _detect_device(self):
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        dtype = torch.bfloat16 if device == "mps" else torch.float32
        return device, dtype
