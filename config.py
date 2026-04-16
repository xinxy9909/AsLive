import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.absolute()

load_dotenv(BASE_DIR / ".env")

# LLM API 配置（OpenAI 兼容格式，默认通义千问）
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen-plus")

# ASR 配置（DashScope Paraformer）
ASR_MODEL_NAME = os.getenv("ASR_MODEL_NAME", "paraformer-realtime-v2")

# TTS 配置（DashScope CosyVoice）
TTS_MODEL_NAME = os.getenv("TTS_MODEL_NAME", "cosyvoice-v1")
TTS_VOICE = os.getenv("TTS_VOICE", "longxiaochun")
TTS_VOICE_MAP = {
    "zf_001": "longxiaochun",
    "zf_002": "loongstella",
    "zm_001": "longwan",
    "zm_002": "longjiangshan",
}

# 其他配置
OUTPUT_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
