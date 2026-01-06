import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.absolute()

# LLM 配置
# 默认路径: "Qwen/Qwen3-4B" /Users/xing/AI/Project/LLM/qwen/Qwen3-4B
LLM_MODEL_PATH = os.getenv("LLM_MODEL_PATH", "Qwen/Qwen3-4B")

# ASR 配置
# 默认模型: "iic/SenseVoiceSmall"
ASR_MODEL_PATH = os.getenv("ASR_MODEL_PATH", "iic/SenseVoiceSmall")

# TTS 配置
# 模型文件通常位于 checkpoints/kokoro/
TTS_MODEL_DIR = BASE_DIR / "checkpoints" / "kokoro"
TTS_CONFIG = {
    "model": str(TTS_MODEL_DIR / "kokoro-v1.1-zh.onnx"),
    "voice": str(TTS_MODEL_DIR / "voices-v1.1-zh.bin"),
    "vocab": str(TTS_MODEL_DIR / "config-v1.1-zh.json")
}

# 其他配置
OUTPUT_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"

# 确保输出目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
