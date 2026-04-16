import dashscope
from dashscope.audio.asr import Recognition
import config


class ASRWrapper:
    def __init__(self):
        print("正在初始化ASR (DashScope Paraformer)...")
        dashscope.api_key = config.LLM_API_KEY
        self.model = config.ASR_MODEL_NAME
        print("ASR初始化完成！")

    def transcribe(self, wav_dir, language="zh", **kwargs):
        print("正在开始ASR识别")
        recognition = Recognition(
            model=self.model,
            callback=None,
            format="opus",
            sample_rate=16000,
            language_hints=[language] if language != "auto" else ["zh", "en"],
        )
        result = recognition.call(wav_dir)
        if result.status_code != 200:
            raise Exception(f"ASR请求失败: {result.message}")
        sentences = result.get_sentence() or []
        text = "".join(s.get("text", "") for s in sentences)
        print("ASR识别结束")
        return text
