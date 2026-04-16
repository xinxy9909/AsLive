"""
Base Agent 类 - 所有 Agent 的基类
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """所有 Agent 的基类"""
    
    def __init__(self, name: str):
        """
        初始化 Agent。
        
        Args:
            name: Agent 名称
        """
        self.name = name
        logger.info(f"Initializing {name} agent")
    
    @abstractmethod
    def inference_stream(self, messages: list[dict]):
        """
        流式推理。
        
        Args:
            messages: 消息列表
            
        Yields:
            推理结果流
        """
        pass
    
    def inference(self, messages: list[dict]) -> str:
        """
        同步推理（完整结果）。
        
        Args:
            messages: 消息列表
            
        Returns:
            完整的推理结果
        """
        return "".join(self.inference_stream(messages))
