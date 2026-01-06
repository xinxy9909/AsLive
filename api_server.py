"""
语音助手 Web API 服务器
基于 FastAPI，提供 SSE 流式响应
"""
import asyncio
import json
import uuid
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import soundfile as sf
import numpy as np

# 导入核心模块
from core.asr import ASRWrapper
from core.llm import LLMWrapper
from core.tts import TTSWrapper
import config

app = FastAPI(title="Voice Assistant API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件与输出目录
STATIC_DIR = config.STATIC_DIR
OUTPUT_DIR = config.OUTPUT_DIR

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

# 全局模型实例（懒加载）
_models = {
    "asr": None,
    "llm": None,
    "tts": None,
    "initialized": False
}

# 对话历史
conversation_history = []

# 句子分隔符
SENTENCE_DELIMITERS = set(',，。！？；.!?;\n')


def get_models():
    """懒加载模型"""
    if not _models["initialized"]:
        print("正在初始化模型...")
        # 现在 Wrapper 会自动使用 config.py 中的默认值
        _models["asr"] = ASRWrapper()
        _models["llm"] = LLMWrapper()
        _models["tts"] = TTSWrapper()
        _models["initialized"] = True
        print("模型初始化完成！")
    return _models["asr"], _models["llm"], _models["tts"]


class ChatRequest(BaseModel):
    text: str
    speak_id: str = "zf_001"
    speed: float = 1.0


def clean_text_for_tts(text: str) -> str:
    """清理文本用于 TTS"""
    import re
    # 如果包含对话格式，提取最后一个助手回复
    if '助手:' in text or '助手：' in text:
        parts = re.split(r'助手[：:]\s*', text)
        if len(parts) > 1:
            last_response = parts[-1]
            last_response = re.split(r'\n\s*用户[：:]', last_response)[0]
            text = last_response
    # 移除角色前缀
    text = re.sub(r'^(用户|助手|User|Assistant)[：:]\s*', '', text, flags=re.MULTILINE)
    return text.strip()


async def process_streaming(user_text: str, speak_id: str = "zf_001", speed: float = 1.0):
    """
    流式处理：LLM 生成 + TTS 合成
    通过 SSE 返回文本和音频 URL
    """
    global conversation_history
    
    asr, llm, tts = get_models()
    
    # 添加用户消息到历史
    conversation_history.append({"role": "user", "content": user_text})
    
    # 构建上下文
    context_messages = conversation_history[-6:]
    
    buffer = ""
    full_response = ""
    audio_files = []
    audio_index = 0
    in_think_tag = False
    
    # 生成唯一会话 ID
    session_id = str(uuid.uuid4())[:8]
    
    # 发送开始事件
    yield f"data: {json.dumps({'type': 'start', 'session_id': session_id})}\n\n"
    
    # 定义异步 TTS 函数
    async def synthesize_and_save(text, index):
        try:
            # 运行在线程池中，避免阻塞事件循环
            def _synthesize():
                phonemes, _ = tts._g2p_model(text)
                samples, sample_rate = tts._kokoro_model.create(
                    phonemes,
                    voice=speak_id,
                    speed=speed,
                    is_phonemes=True
                )
                return samples, sample_rate

            samples, sample_rate = await asyncio.to_thread(_synthesize)
            
            # 保存音频文件
            audio_filename = f"{session_id}_{index}.wav"
            audio_path = OUTPUT_DIR / audio_filename
            # 写入文件也是 IO 操作，也可以放到线程池
            await asyncio.to_thread(sf.write, str(audio_path), samples, sample_rate)
            
            return audio_filename
        except Exception as e:
            print(f"TTS Error: {e}")
            return None

    # 流式生成
    for chunk in llm.inference_stream_chat(context_messages):
        full_response += chunk
        
        # 发送文本片段
        yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
        
        # 处理 <think> 标签
        if '<think>' in chunk:
            in_think_tag = True
            before_think = chunk.split('<think>')[0]
            if before_think:
                buffer += before_think
            continue
        
        if '</think>' in chunk:
            in_think_tag = False
            after_think = chunk.split('</think>')[-1]
            if after_think:
                buffer += after_think
            continue
            
        if in_think_tag:
            continue
            
        buffer += chunk
        
        # 检测句子边界
        while True:
            delimiter_pos = -1
            for i, char in enumerate(buffer):
                if char in SENTENCE_DELIMITERS:
                    delimiter_pos = i
                    break
            
            if delimiter_pos == -1:
                break
            
            # 提取句子
            sentence = buffer[:delimiter_pos + 1]
            buffer = buffer[delimiter_pos + 1:]
            
            # 清理并合成 TTS
            clean_text = clean_text_for_tts(sentence)
            if clean_text:
                audio_filename = await synthesize_and_save(clean_text, audio_index)
                if audio_filename:
                    yield f"data: {json.dumps({'type': 'audio', 'url': f'/outputs/{audio_filename}', 'text': clean_text})}\n\n"
                    audio_index += 1
        
        # 让出控制权
        await asyncio.sleep(0)
    
    # 处理剩余内容
    if buffer.strip():
        clean_text = clean_text_for_tts(buffer)
        if clean_text:
            audio_filename = await synthesize_and_save(clean_text, audio_index)
            if audio_filename:
                yield f"data: {json.dumps({'type': 'audio', 'url': f'/outputs/{audio_filename}', 'text': clean_text})}\n\n"
    
    # 保存助手回复到历史
    clean_response = clean_text_for_tts(full_response)
    conversation_history.append({"role": "assistant", "content": clean_response.strip()})
    
    # 发送结束事件
    yield f"data: {json.dumps({'type': 'end', 'full_response': clean_response})}\n\n"


@app.get("/")
async def index():
    """返回主页"""
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/chat")
async def chat(request: ChatRequest):
    """文本聊天接口，返回 SSE 流"""
    print(f"收到文本请求: {request.text}")
    return StreamingResponse(
        process_streaming(request.text, request.speak_id, request.speed),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.post("/audio")
async def audio_chat(
    audio: UploadFile = File(...),
    speak_id: str = "zf_001",
    speed: float = 1.0
):
    """语音聊天接口"""
    asr, llm, tts = get_models()
    
    # 保存上传的音频
    temp_path = OUTPUT_DIR / f"temp_{uuid.uuid4()}.wav"
    content = await audio.read()
    with open(temp_path, "wb") as f:
        f.write(content)
    
    try:
        # ASR 识别
        user_text = asr.transcribe(wav_dir=str(temp_path))
        
        # 删除临时文件
        os.remove(temp_path)
        
        if not user_text.strip():
            raise HTTPException(status_code=400, detail="未识别到有效语音")
        
        # 返回识别结果和流式响应
        async def generate():
            # 先发送识别结果
            yield f"data: {json.dumps({'type': 'asr', 'text': user_text})}\n\n"
            
            # 然后进行流式处理
            async for event in process_streaming(user_text, speak_id, speed):
                yield event
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    except Exception as e:
        if temp_path.exists():
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history():
    """获取对话历史"""
    return {"history": conversation_history}


@app.delete("/history")
async def clear_history():
    """清空对话历史"""
    global conversation_history
    conversation_history = []
    return {"status": "ok"}


@app.on_event("startup")
async def startup():
    """启动时预加载模型"""
    print("服务器启动中...")
    print("正在预加载模型，请稍候...")
    # 预加载模型，避免第一次请求卡顿
    get_models()
    print("服务器启动完成，模型已就绪！")


if __name__ == "__main__":
    import uvicorn
    # 开启热重载，方便开发调试
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
