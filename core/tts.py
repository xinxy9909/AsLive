"""
TTS：基于 DashScope CosyVoice 的中文语音合成
"""
import asyncio
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer
import config


class TTSWrapper:
    def __init__(self, tts_config: dict = None):
        dashscope.api_key = config.LLM_API_KEY
        self.model = config.TTS_MODEL_NAME
        self.default_voice = (tts_config or {}).get("voice", config.TTS_VOICE)
        print("TTS (DashScope CosyVoice) 初始化完成！")

    def _resolve_voice(self, speak_id: str = None) -> str:
        if speak_id and speak_id in config.TTS_VOICE_MAP:
            return config.TTS_VOICE_MAP[speak_id]
        return self.default_voice

    def _synthesize(self, text: str, voice: str, speed: float = 1.0) -> bytes:
        synthesizer = SpeechSynthesizer(
            model=self.model,
            voice=voice,
            speech_rate=speed,
        )
        audio = synthesizer.call(text)
        if audio is None:
            raise RuntimeError("TTS合成失败：API未返回音频数据")
        return bytes(audio)

    async def synthesize_async(self, text: str, speak_id: str = None, speed: float = 1.0) -> bytes:
        """异步合成，返回 MP3 字节数据"""
        voice = self._resolve_voice(speak_id)
        return await asyncio.to_thread(self._synthesize, text, voice, speed)

    def inference(self, text: str, out_dir: str = "output", speak_id: str = None, speed: float = 1.0, **kwargs) -> str:
        voice = self._resolve_voice(speak_id)
        mp3_data = self._synthesize(text, voice)
        output_path = f"{out_dir}_output.mp3"
        with open(output_path, "wb") as f:
            f.write(mp3_data)
        return output_path
