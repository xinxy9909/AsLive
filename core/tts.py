"""
TTS：基于 Kokoro ONNX 的中文语音合成
支持：
1. 流式合成（边生成边播放）
2. 基于说话人ID的合成
"""
import soundfile as sf
import numpy as np
import sounddevice as sd
import time
import threading
import queue
from pathlib import Path
from typing import Optional
import config

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class TTSWrapper:
    def __init__(self, tts_config: dict = None):
        self.kokoro_paths = tts_config if tts_config else config.TTS_CONFIG
        
        # 验证文件存在
        for key, path in self.kokoro_paths.items():
            if not Path(path).exists():
                raise FileNotFoundError(f"Kokoro resource not found: {path}")
        
        # 懒加载模型
        self._kokoro_model = None
        self._g2p_model = None
        
        # 音频播放队列（用于流式播放）
        self.audio_queue = queue.Queue()
        self.playback_thread = None
        self.stop_playback = False
        self.all_audio_chunks = []
        
        print("正在加载Kokoro TTS模型...")
        self._load_models()
        print("Kokoro TTS模型加载完成！")
    
    def _load_models(self):
        """加载 Kokoro 和 G2P 模型"""
        from misaki import zh
        from kokoro_onnx import Kokoro
        
        self._g2p_model = zh.ZHG2P(version="1.1")
        self._kokoro_model = Kokoro(
            model_path=self.kokoro_paths["model"],
            voices_path=self.kokoro_paths["voice"],
            vocab_config=self.kokoro_paths["vocab"]
        )
    
    @property
    def sample_rate(self) -> int:
        """返回采样率"""
        return 24000  # Kokoro 默认采样率
    
    def _playback_worker(self):
        """后台线程：从队列中取出音频并播放"""
        while not self.stop_playback or not self.audio_queue.empty():
            try:
                audio_chunk = self.audio_queue.get(timeout=0.1)
                if audio_chunk is not None:
                    sd.play(audio_chunk, samplerate=self.sample_rate)
                    sd.wait()
                self.audio_queue.task_done()
            except queue.Empty:
                continue
    
    def start_streaming_session(self):
        """开始一个新的流式TTS会话"""
        self.stop_playback = False
        self.all_audio_chunks = []
        self.playback_thread = threading.Thread(target=self._playback_worker, daemon=True)
        self.playback_thread.start()
    
    def stream_sentence(self, text: str, speak_id: str = "zf_001", speed: float = 1.0):
        """
        流式合成并播放一个句子（非阻塞）
        
        Args:
            text: 要合成的文本
            speak_id: 说话人ID
            speed: 语速 (0.5 - 2.0)
        """
        if not text.strip():
            return
        
        try:
            # 文本转音素
            phonemes, _ = self._g2p_model(text)
            
            # 合成音频
            samples, sample_rate = self._kokoro_model.create(
                phonemes,
                voice=speak_id,
                speed=speed,
                is_phonemes=True
            )
            
            # 放入播放队列
            self.audio_queue.put(samples)
            
            # 保存用于最终合并
            self.all_audio_chunks.append(samples)
            
        except Exception as e:
            print(f"TTS合成失败: {e}")
    
    def finish_streaming_session(self, out_dir: str = "output"):
        """结束流式会话，等待播放完成并保存音频"""
        self.stop_playback = True
        if self.playback_thread:
            self.playback_thread.join(timeout=30)
        
        # 保存完整音频
        if self.all_audio_chunks:
            wav = np.concatenate(self.all_audio_chunks)
            output_path = f"{out_dir}_streaming.wav"
            sf.write(output_path, wav, self.sample_rate)
            print(f"流式TTS完成，已保存: {output_path}")
    
    def inference(
        self,
        text: str,
        out_dir: str = "output",
        speak_id: str = "zf_001",
        speed: float = 1.0,
        is_stream: bool = False
    ) -> Optional[str]:
        """
        语音合成
        
        Args:
            text: 输入文本
            out_dir: 输出文件路径前缀
            speak_id: 说话人ID
            speed: 语速 (0.5 - 2.0)
            is_stream: 是否流式播放
            
        Returns:
            str: 生成的音频文件路径
        """
        if not text:
            print("输入文本为空")
            return None
        
        try:
            t1 = time.time()
            
            # 文本转音素
            phonemes, _ = self._g2p_model(text)
            
            # 合成音频
            samples, sample_rate = self._kokoro_model.create(
                phonemes,
                voice=speak_id,
                speed=speed,
                is_phonemes=True
            )
            
            if is_stream:
                # 流式播放
                sd.play(samples, samplerate=sample_rate)
                sd.wait()
                output_path = f"{out_dir}_streaming.wav"
            else:
                output_path = f"{out_dir}_output.wav"
            
            sf.write(output_path, samples, sample_rate)
            print(f"TTS完成，耗时: {time.time() - t1:.2f}秒，已保存: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"TTS合成失败: {e}")
            return None


if __name__ == "__main__":
    tts = KokoroTTS()
    text = '''
            总有人说，身为传统工业大省的山东，错过了互联网，错过了新经济，错过了很多新兴产业的最佳介入期。
            眼下，即将迈过经济"10万亿"台阶的山东，终于赶上了风口。
    '''
    tts.inference(text=text, is_stream=True, out_dir="./")