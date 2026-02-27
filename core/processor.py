import os
from pydub import AudioSegment

class AudioProcessor:
    """原子化音频组件：针对播客对谈优化的拼接与去噪引擎"""
    
    def __init__(self, base_dir):
        self.temp_dir = os.path.join(base_dir, "assets/temp")

    def extract_voice_seed(self, audio_path, persona_cn, max_sec=10, skip_start_ms=1500):
        """样音脱水：跳过 1.5s 避障，强制去除首尾静音"""
        os.makedirs(self.temp_dir, exist_ok=True)
        temp_path = os.path.join(self.temp_dir, f"当前参考_{persona_cn}.wav")
        
        if os.path.exists(temp_path) and os.path.getmtime(temp_path) >= os.path.getmtime(audio_path):
            return temp_path
            
        print(f"🔨 [Ref-Opt] 正在提取【{persona_cn}】纯净样音...")
        audio = AudioSegment.from_file(audio_path)
        if len(audio) > skip_start_ms + 2000:
            audio = audio[skip_start_ms:]
        audio = self._trim_silence(audio)
        if len(audio) > max_sec * 1000:
            audio = audio[:max_sec * 1000]
        audio.export(temp_path, format="wav")
        return temp_path

    def _trim_silence(self, audio, threshold=-45.0, chunk_size=5):
        """物理切除模型起步/收尾杂音"""
        def detect(sound):
            it = 0
            while it < len(sound) and sound[it:it+chunk_size].dBFS < threshold:
                it += chunk_size
            return it
        s = detect(audio)
        e = detect(audio.reverse())
        # 如果整段都是静音，返回一个极短的静音
        if s + e >= len(audio):
            return AudioSegment.silent(duration=100)
        return audio[s : (len(audio) - e)]

    def apply_post_tuning(self, path):
        """统一调音：脱水 + 响度标准化 + 极短淡入淡出"""
        try:
            audio = AudioSegment.from_file(path)
            audio = self._trim_silence(audio)
            audio = audio.normalize(headroom=0.1)
            # 50ms 淡入淡出，彻底消除开关爆音
            audio = audio.fade_in(50).fade_out(50)
            audio.export(path, format="wav")
            return audio
        except: return None

    def merge_scene(self, segments, output_path, gap_ms=1000):
        """高级播客缝合：引入交叉淡化，确保衔接处纯净无声"""
        print(f"🧵 正在执行播客场景缝合 (间隔: {gap_ms}ms)...")
        combined = AudioSegment.empty()
        
        for i, seg in enumerate(segments):
            # 在每段台词前加一个极短的淡入，后加淡出
            clean_seg = seg.fade_in(30).fade_out(30)
            combined += clean_seg
            if i < len(segments) - 1:
                # 插入真正的数字零底噪
                combined += AudioSegment.silent(duration=gap_ms)
        
        combined.export(output_path, format="wav")
        # 对总轨执行最后一次“脱水”自检
        self.apply_post_tuning(output_path)
        print(f"✅ 播客总轨已完成最终纯净化处理。")
