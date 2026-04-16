"""
Monitor Agent - 视频监控智能Agent
支持通过自然语言控制视频监控设备
"""

import json
import logging
import os
from typing import Generator, Optional

import requests

from .base_agent import BaseAgent
from .monitor_state import MonitorState
from .monitor_tools import MonitorTools

logger = logging.getLogger(__name__)

# 配置
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen-plus")
MONITOR_MODEL_NAME = os.getenv("MONITOR_MODEL_NAME", "qwen-plus")


class MonitorAgent(BaseAgent):
    """监控Agent - 管理视频监控的智能助手"""
    
    SYSTEM_PROMPT = """你是一个专业的视频监控管理助手。你能够帮助用户管理和控制视频监控系统。

你可以执行以下操作：
1. 列出指定平台的所有摄像头
2. 放大/缩放指定摄像头的画面
3. 隐藏或显示摄像头
4. 获取摄像头状态信息

当用户提出请求时，请分析用户的意图，并调用相应的工具来完成请求。

重要提示：
- 当用户说"放大"、"全屏"、"看"某个摄像头时，使用 zoom_camera 工具
- 当用户说"隐藏"、"关闭"某个摄像头时，使用 hide_camera 工具
- 当用户说"显示"、"打开"某个摄像头时，使用 show_camera 工具
- 当用户询问"有哪些摄像头"、"列出"时，使用 list_cameras 工具
- 当用户询问"状态"、"怎么样"时，使用 get_camera_status 工具
- 摄像头名称包括：JinLiLite1, JinLiLite2, JinLiLite3, ChiWen1, ChiWen2, ChiWen3
- 平台名称包括：JinLiLite, ChiWen

请确保你的回复清晰、准确，并及时反馈操作结果。"""
    
    def __init__(self, name: str = "MonitorAgent"):
        """
        初始化Monitor Agent。
        
        Args:
            name: Agent名称
        """
        super().__init__(name)
        self.state = MonitorState()
        self.tools = MonitorTools(self.state)
        logger.info(f"MonitorAgent initialized with {len(self.state.get_all_cameras())} cameras")
    
    def inference_stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """
        流式推理 - 与LLM交互，支持工具调用。
        
        Args:
            messages: 消息列表
            
        Yields:
            推理结果流（文本或JSON格式的工具动作事件）
        """
        # 构建发送给LLM的消息
        llm_messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT
            }
        ]
        llm_messages.extend(messages)
        
        # 循环直到完成（无更多工具调用）
        while True:
            try:
                # 调用LLM
                response = requests.post(
                    f"{LLM_BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {LLM_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": MONITOR_MODEL_NAME,
                        "messages": llm_messages,
                        "tools": self.tools.get_tools_definition(),
                        "tool_choice": "auto",
                        "stream": False,
                    },
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                message = result["choices"][0]["message"]
                
                # 返回助手的文本内容
                if "content" in message and message["content"]:
                    yield message["content"]
                
                # 检查是否有工具调用
                if "tool_calls" not in message or not message["tool_calls"]:
                    # 没有工具调用，推理完成
                    break
                
                # 处理工具调用
                llm_messages.append(message)
                
                tool_results = []
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_input = json.loads(tool_call["function"]["arguments"])
                    
                    logger.info(f"Calling tool: {tool_name} with input: {tool_input}")
                    
                    # 执行工具
                    tool_result = self.tools.execute_tool(tool_name, tool_input)
                    
                    logger.info(f"Tool result: {tool_result}")
                    
                    # **关键：向前端发送工具执行结果**
                    # 以JSON格式发送，前端会识别并处理
                    tool_action_event = {
                        "type": "tool_action",
                        "tool_name": tool_name,
                        "tool_input": tool_input,
                        "tool_result": tool_result
                    }
                    yield json.dumps(tool_action_event, ensure_ascii=False)
                    
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": tool_name,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    })
                
                # 添加工具结果到消息列表
                llm_messages.extend(tool_results)
            
            except requests.exceptions.RequestException as e:
                logger.error(f"LLM request error: {e}")
                yield f"错误：无法连接到LLM服务。{str(e)}"
                break
            
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                yield f"错误：响应解析失败。{str(e)}"
                break
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                yield f"错误：{str(e)}"
                break
    
    def get_state(self) -> dict:
        """获取当前的监控状态"""
        return self.state.get_status_dict()
    
    def reset_state(self):
        """重置监控状态"""
        self.state = MonitorState()
        self.tools = MonitorTools(self.state)
        logger.info("Monitor state reset")
