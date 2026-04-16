"""
LLM 包装器 - 意图识别和 Agent 路由
"""

import logging
import os
import uuid

from core.agents import AINetiveAgent, OrganoidAgent

logger = logging.getLogger(__name__)


# Agent 类型枚举
class AgentType:
    """Agent 类型常量"""
    AI_NATIVE = "ai-native"
    ORGANOID = "organoid"


# 配置
DEFAULT_AGENT = os.getenv("DEFAULT_AGENT", AgentType.AI_NATIVE)

# Agent 实例缓存
_agents = {
    AgentType.AI_NATIVE: AINetiveAgent(),
    AgentType.ORGANOID: OrganoidAgent(),
}


class IntentClassifier:
    """
    意图识别器 - 使用 LLM 识别用户意图并选择合适的 Agent
    """
    
    # 意图描述
    INTENT_DESCRIPTIONS = {
        AgentType.ORGANOID: "多模态推理 - 用户的问题需要进行深度推理和多步骤分析",
        AgentType.AI_NATIVE: "通用对话 - 一般性聊天、日常对话和简单问答",
    }
    
    def classify(self, text: str) -> str:
        """
        使用 LLM 识别用户输入的意图，并返回最适合的 Agent 类型。
        
        Args:
            text: 用户输入的文本
            
        Returns:
            选择的 Agent 类型
        """
        if not text or not isinstance(text, str):
            logger.warning("Invalid input text for intent classification")
            return DEFAULT_AGENT
        
        try:
            # 构建意图识别的 prompt
            agent_options = "\n".join([
                f"- {agent_type}: {desc}" 
                for agent_type, desc in self.INTENT_DESCRIPTIONS.items()
            ])
            
            prompt = f"""请分析用户的这个问题，判断最适合用哪种Agent来处理。

可选的Agent类型：
{agent_options}

用户问题："{text}"

请只返回一个Agent的名称（ai-native 或 organoid），不要返回其他内容。"""
            
            # 使用 AI-Native Agent 进行意图识别
            ai_native = _agents[AgentType.AI_NATIVE]
            messages = [{"role": "user", "content": prompt}]
            
            result = ""
            for chunk in ai_native.inference_stream(messages):
                result += chunk
            
            result = result.strip().lower()
            logger.info(f"Intent classification result: {result}")
            
            # 解析结果，匹配 Agent 类型
            if "organoid" in result:
                logger.info(f"Selected agent: organoid for query: {text[:50]}...")
                return AgentType.ORGANOID
            elif "ai-native" in result or "ai native" in result:
                logger.info(f"Selected agent: ai-native for query: {text[:50]}...")
                return AgentType.AI_NATIVE
            
            # 如果解析失败，使用默认 Agent
            logger.warning(f"Failed to parse intent result: {result}, using default agent")
            return DEFAULT_AGENT
            
        except Exception as e:
            logger.error(f"Error in intent classification: {e}, using default agent")
            return DEFAULT_AGENT


# 全局意图分类器
_intent_classifier = IntentClassifier()


class LLMWrapper:
    """
    LLM 包装器 - 支持意图识别和多 Agent 路由
    """
    
    def __init__(self, enable_intent_classification: bool = True):
        """
        初始化 LLMWrapper。
        
        Args:
            enable_intent_classification: 是否启用意图识别来自动选择 Agent
        """
        print("正在初始化LLM (支持意图识别 + 多 Agent 路由)...")
        self.enable_intent_classification = enable_intent_classification
        self.current_agent = DEFAULT_AGENT
        print(f"默认 Agent: {DEFAULT_AGENT}")
        print("LLM初始化完成！")
    
    def select_agent(self, text: str) -> str:
        """
        根据用户输入选择最适合的 Agent。
        
        Args:
            text: 用户输入文本
            
        Returns:
            选择的 Agent 类型
        """
        if not self.enable_intent_classification:
            return DEFAULT_AGENT
        
        selected = _intent_classifier.classify(text)
        self.current_agent = selected
        return selected
    
    def inference(self, text: str, max_new_tokens: int = 500) -> str:
        """
        同步推理接口（完整结果）。
        
        Args:
            text: 输入文本
            max_new_tokens: 最大生成token数（未使用，保留以兼容旧接口）
            
        Returns:
            生成的文本
        """
        return "".join(self.inference_stream(text, max_new_tokens))
    
    def inference_stream(self, text: str, max_new_tokens: int = 500):
        """
        流式推理接口（单轮对话）。
        
        Args:
            text: 输入文本
            max_new_tokens: 最大生成token数（未使用，保留以兼容旧接口）
            
        Yields:
            推理结果流
        """
        # 选择 Agent
        agent_type = self.select_agent(text)
        logger.info(f"Processing with agent: {agent_type}")
        
        # 获取 Agent 实例
        agent = _agents.get(agent_type, _agents[AgentType.AI_NATIVE])
        
        # 构建消息
        messages = [{"role": "user", "content": text}]
        
        # 执行推理
        yield from agent.inference_stream(messages)
    
    def inference_stream_chat(self, messages: list, max_new_tokens: int = 500, 
                             use_intent_classification: bool = True):
        """
        流式推理接口（多轮对话）。
        
        Args:
            messages: 消息列表
            max_new_tokens: 最大生成token数（未使用，保留以兼容旧接口）
            use_intent_classification: 是否对最后一条用户消息进行意图识别
            
        Yields:
            推理结果流
        """
        # 获取最后一条用户消息用于意图识别
        user_msgs = [m for m in messages if m.get("role") == "user"]
        query = user_msgs[-1]["content"] if user_msgs else ""
        
        # 根据是否启用意图识别来选择 Agent
        if use_intent_classification and self.enable_intent_classification:
            agent_type = self.select_agent(query)
        else:
            agent_type = DEFAULT_AGENT
        
        logger.info(f"Processing chat with agent: {agent_type}")
        
        # 获取 Agent 实例
        agent = _agents.get(agent_type, _agents[AgentType.AI_NATIVE])
        
        # 执行推理
        yield from agent.inference_stream(messages)
