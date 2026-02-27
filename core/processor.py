import os
from pydub import AudioSegment

class AudioProcessor:
    """原子化音频组件：负责样音提取、格式中转、后期调音及对话缝合"""
    
    def __init__(self, base_dir):
        self.temp_dir = os.path.join(base_dir, "assets/temp")
        self.out_dir = os.path.join(base_dir, "assets/output_audio")
        self.pod_dir = os.path.join(base_dir, "assets/podcast_output")

    def extract_voice_seed(self, audio_path, persona_cn, max_sec=10, skip_start_ms=1500):
        """【独立功能：Ref-Opt】提取纯净样音到 temp"""
        os.makedirs(self.temp_dir, exist_ok=True)
        temp_path = os.path.join(self.temp_dir, f"当前参考_{persona_cn}.wav")
        
        if os.path.exists(temp_path) and os.path.getmtime(temp_path) >= os.path.getmtime(audio_path):
            return temp_path
            
        print(f"🔨 [Ref-Opt] 正在为【{persona_cn}】提取黄金人声样音...")
        audio = AudioSegment.from_file(audio_path)
        # 安全偏移
        if len(audio) > skip_start_ms + 2000:
            audio = audio[skip_start_ms:]
        # 脱水去噪
        audio = self._trim_silence(audio)
        # 裁剪
        if len(audio) > max_sec * 1000:
            audio = audio[:max_sec * 1000]
        audio.export(temp_path, format="wav")
        return temp_path

    def _trim_silence(self, audio, threshold=-50.0, chunk_size=5):
        def detect(sound):
            it = 0
            while it < len(sound) and sound[it:it+chunk_size].dBFS < threshold:
                it += chunk_size
            return it
        s = detect(audio)
        e = detect(audio.reverse())
        return audio[s : (len(audio) - e)]

    def apply_post_tuning(self, path, mode="movie", add_padding=True):
        """【独立功能：Post-Tune】成品后期优化"""
        try:
            audio = AudioSegment.from_file(path)
            audio = self._trim_silence(audio)
            audio = audio.normalize(headroom=0.1).fade_in(50).fade_out(50)
            if add_padding:
                s_ms = 1500 if mode == "podcast" else 1500
                audio = AudioSegment.silent(duration=s_ms) + audio + AudioSegment.silent(duration=1000)
            audio.export(path, format="wav")
            return audio
        except: return None

    def merge_scene(self, segments, output_path, gap_ms=800):
        """【独立功能：缝合】"""
        combined = AudioSegment.silent(duration=1500)
        for i, seg in enumerate(segments):
            combined += seg
            if i < len(segments) - 1: combined += AudioSegment.silent(duration=gap_ms)
        combined += AudioSegment.silent(duration=1000)
        combined.export(output_path, format="wav")
