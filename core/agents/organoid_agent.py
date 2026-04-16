"""
Organoid Agent - 类器官多模态推理 Agent
"""

import json
import logging
import os
import uuid

import requests

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

# 配置
ORGANOID_BASE_URL = os.getenv("ORGANOID_BASE_URL", "http://192.168.1.97:2026")
ORGANOID_MODEL = os.getenv("ORGANOID_MODEL", "qwen-plus")
ORGANOID_THINKING_ENABLED = os.getenv("ORGANOID_THINKING_ENABLED", "true").lower() == "true"
ORGANOID_CONFIG_NAME = os.getenv("ORGANOID_CONFIG_NAME", "mega_agent")


def _submit_chat(thread_id: str, messages: list[dict]) -> str:
    """
    向类器官 Agent 提交聊天请求。
    
    Args:
        thread_id: 对话线程 ID
        messages: 消息列表
        
    Returns:
        响应内容
    """
    url = f"{ORGANOID_BASE_URL}/api/chat/submit"
    headers = {
        "User-Agent": "AsLive/1.0",
        "Content-Type": "application/json",
        "Accept": "*/*",
    }
    
    payload = {
        "thread_id": thread_id,
        "messages": messages,
        "model": ORGANOID_MODEL,
        "thinking_enabled": ORGANOID_THINKING_ENABLED,
        "plan_mode": False,
        "config_name": ORGANOID_CONFIG_NAME,
    }
    
    logger.info(f"Organoid: Submitting chat to {url}")
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    
    return resp.text


def _resume_chat(thread_id: str, offset: int = 0) -> requests.Response:
    """
    从类器官 Agent 拉取聊天流（SSE）。
    
    Args:
        thread_id: 对话线程 ID
        offset: 消息偏移量（0 表示拉取全部历史）
        
    Returns:
        SSE 流式响应
    """
    url = f"{ORGANOID_BASE_URL}/api/chat/resume/{thread_id}?offset={offset}"
    headers = {
        "User-Agent": "AsLive/1.0",
        "Accept": "*/*",
    }
    
    logger.info(f"Organoid: Resuming chat from {url}")
    resp = requests.get(url, headers=headers, stream=True, timeout=60)
    resp.raise_for_status()
    return resp


def _parse_sse(response: requests.Response, only_latest: bool = False):
    """
    解析类器官 Agent SSE 响应流。
    
    只处理 event:message 的消息，并且只输出 type 为 ai 的内容。
    同时从 event:end 中获取 total_rounds 用于下次拉取。
    
    Args:
        response: SSE 响应对象
        only_latest: 如果为 True，仅返回最新消息；如果为 False，返回全部 AI 消息
        
    Yields:
        content 字符串
    """
    current_event = None
    total_rounds = 0
    ai_message_count = 0
    messages = []
    
    for raw_line in response.iter_lines(decode_unicode=True):
        if not raw_line:
            continue
        
        # 解析 event 字段
        if raw_line.startswith("event:"):
            current_event = raw_line[len("event:"):].strip()
            logger.debug(f"Received event: {current_event}")
            continue
        
        # 解析 data 字段
        if raw_line.startswith("data:"):
            data_str = raw_line[len("data:"):].strip()
            
            # 处理流结束标记
            if data_str == "[DONE]":
                logger.debug("Received [DONE] marker")
                break
            
            # 处理 end 事件，获取 total_rounds 信息
            if current_event == "end":
                try:
                    end_data = json.loads(data_str)
                    total_rounds = end_data.get("total_rounds", 0)
                    logger.info(f"Organoid: Received total_rounds={total_rounds}")
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse end event: {data_str}")
                continue
            
            # 只处理 message 类型的事件
            if current_event == "message":
                try:
                    current_data = json.loads(data_str)
                    
                    # 只输出 type 为 ai 的消息
                    if current_data.get("type") == "ai":
                        content = current_data.get("data", "")
                        if content:
                            ai_message_count += 1
                            logger.debug(f"Yielding AI message #{ai_message_count}: {content[:50]}...")
                            messages.append(content)
                    else:
                        logger.debug(f"Skipping non-AI message, type: {current_data.get('type')}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {data_str}, error: {e}")
            else:
                logger.debug(f"Skipping non-message event: {current_event}")
    
    # 根据 only_latest 标志决定返回哪些消息
    if only_latest and total_rounds > 0:
        # 仅返回最新消息（位置为 total_rounds）
        if len(messages) > 0:
            yield messages[-1]
    else:
        # 返回全部消息
        for msg in messages:
            yield msg





class OrganoidAgent(BaseAgent):
    """类器官多模态推理 Agent 实现"""
    
    def __init__(self):
        """初始化 Organoid Agent"""
        super().__init__("Organoid")
        # 记录上次的 total_rounds，用于下次拉取时作为 offset
        self._last_total_rounds = 0
    
    def inference_stream(self, messages: list[dict]):
        """
        流式推理（Organoid Agent）。
        
        每次调用只拉取最新的消息（使用上次的 total_rounds 作为 offset）。
        
        Args:
            messages: 消息列表，格式为 [{"role": "user"/"assistant", "content": "..."}]
            
        Yields:
            推理结果流（仅包含最新的 AI 回复）
        """
        thread_id = str(uuid.uuid4())
        
        try:
            # 获取用户最后一条消息用于日志
            user_msgs = [m for m in messages if m.get("role") == "user"]
            query = user_msgs[-1]["content"] if user_msgs else ""
            logger.info(f"Organoid: Processing query: {query[:50]}...")
            
            # 步骤1: 向类器官 Agent 提交聊天请求
            _submit_chat(thread_id, messages)
            logger.info(f"Organoid: Chat submitted with thread_id: {thread_id}")
            
            # 步骤2: 从类器官 Agent 拉取聊天流
            # 使用上次的 total_rounds 作为 offset，只拉取最新的消息
            current_offset = self._last_total_rounds
            logger.info(f"Organoid: Resuming chat with offset={current_offset} (只拉取最新消息)")
            resp = _resume_chat(thread_id, offset=current_offset)
            
            try:
                # 解析 SSE 并获取最新的消息
                for content in _parse_sse(resp, only_latest=False):
                    yield content
                    
                logger.info(f"Organoid: Completed streaming for thread_id: {thread_id}")
                
            finally:
                resp.close()
                
        except Exception as e:
            logger.error(f"Organoid Agent error: {e}")
            raise
    
    def get_last_total_rounds(self) -> int:
        """
        获取最后一次推理的 total_rounds（当前的 offset）。
        
        Returns:
            上次推理后的总回合数
        """
        return self._last_total_rounds
    
    def set_last_total_rounds(self, total_rounds: int) -> None:
        """
        设置 total_rounds（用于测试或手动管理偏移量）。
        
        Args:
            total_rounds: 要设置的 total_rounds 值
        """
        self._last_total_rounds = total_rounds
        logger.info(f"Organoid: Set total_rounds to {total_rounds}")
    
    def reset_offset(self) -> None:
        """
        重置偏移量为 0，用于需要拉取全部历史的场景。
        
        注意：通常不需要调用此方法，系统会自动管理偏移量。
        """
        self._last_total_rounds = 0
        logger.info("Organoid: Offset reset to 0")


