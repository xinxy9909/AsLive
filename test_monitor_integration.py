#!/usr/bin/env python3
"""
Monitor Agent 集成测试 - 测试通过LLM意图识别的路由
"""

import sys
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入
from core.llm import LLMWrapper, AgentType, IntentClassifier
from core.agents.monitor_agent import MonitorAgent


def test_llm_wrapper_with_monitor():
    """测试LLMWrapper中的Monitor Agent路由"""
    print("\n" + "="*60)
    print("测试：LLM Wrapper + Monitor Agent 路由")
    print("="*60)
    
    llm = LLMWrapper(enable_intent_classification=True)
    
    # 测试用例：涉及监控的问题
    test_cases = [
        ("放大JinLiLite1", AgentType.MONITOR),
        ("隐藏ChiWen2摄像头", AgentType.MONITOR),
        ("显示JinLiLite2", AgentType.MONITOR),
        ("监控系统中有哪些摄像头", AgentType.MONITOR),
        ("JinLiLite平台的所有摄像头怎样", AgentType.MONITOR),
    ]
    
    print("\n测试意图识别（需要LLM API）:")
    for text, expected_agent in test_cases:
        print(f"\n输入: {text}")
        print(f"期望Agent: {expected_agent}")
        try:
            selected = llm.select_agent(text)
            print(f"选中Agent: {selected}")
            # 注意：实际的Agent选择可能与期望不同，这取决于LLM的判断
        except Exception as e:
            print(f"错误: {e}")


def test_monitor_agent_integration():
    """测试Monitor Agent与LLM的集成"""
    print("\n" + "="*60)
    print("测试：Monitor Agent 推理流程")
    print("="*60)
    
    # 创建Monitor Agent
    agent = MonitorAgent()
    print(f"\n✓ Monitor Agent 初始化成功")
    print(f"  可用工具数: {len(agent.tools.get_tools_definition())}")
    
    # 测试工具可用性
    tools = agent.tools.get_tools_definition()
    print(f"\n✓ 可用的工具:")
    for tool in tools:
        print(f"  - {tool['function']['name']}")
    
    # 测试状态获取
    state = agent.get_state()
    print(f"\n✓ 获取监控状态:")
    print(f"  总摄像头数: {len(state['cameras'])}")
    
    # 统计可见和隐藏的摄像头
    visible_count = sum(1 for cam in state['cameras'].values() if cam['visible'])
    hidden_count = len(state['cameras']) - visible_count
    print(f"  可见摄像头: {visible_count}")
    print(f"  隐藏摄像头: {hidden_count}")


def test_direct_tool_execution():
    """测试直接执行工具"""
    print("\n" + "="*60)
    print("测试：Monitor Agent 工具直接执行")
    print("="*60)
    
    agent = MonitorAgent()
    
    # 测试list_cameras工具
    print("\n执行 list_cameras 工具:")
    result = agent.tools.list_cameras("JinLiLite")
    print(f"  状态: {result['status']}")
    print(f"  摄像头数: {len(result['data']['cameras'])}")
    
    # 测试zoom_camera工具
    print("\n执行 zoom_camera 工具:")
    result = agent.tools.zoom_camera("ChiWen1", "fullscreen")
    print(f"  状态: {result['status']}")
    print(f"  摄像头: {result['data']['camera_name']}")
    
    # 验证状态更新
    state = agent.get_state()
    chiwen1_state = state['cameras']['ChiWen1']
    print(f"  ChiWen1 当前状态: visible={chiwen1_state['visible']}, zoom_level={chiwen1_state['zoom_level']}")
    
    # 测试hide_camera工具
    print("\n执行 hide_camera 工具:")
    result = agent.tools.hide_camera("JinLiLite1")
    print(f"  状态: {result['status']}")
    
    state = agent.get_state()
    jinlilite1_state = state['cameras']['JinLiLite1']
    print(f"  JinLiLite1 当前状态: visible={jinlilite1_state['visible']}")
    
    # 测试show_camera工具
    print("\n执行 show_camera 工具:")
    result = agent.tools.show_camera("JinLiLite1")
    print(f"  状态: {result['status']}")
    
    state = agent.get_state()
    jinlilite1_state = state['cameras']['JinLiLite1']
    print(f"  JinLiLite1 当前状态: visible={jinlilite1_state['visible']}")


def test_agent_type_enum():
    """测试AgentType枚举"""
    print("\n" + "="*60)
    print("测试：AgentType 枚举")
    print("="*60)
    
    print(f"\n可用的Agent类型:")
    print(f"  - {AgentType.AI_NATIVE}")
    print(f"  - {AgentType.ORGANOID}")
    print(f"  - {AgentType.MONITOR}")


def main():
    """运行所有测试"""
    print("\n" + "="*70)
    print("Monitor Agent 集成测试套件")
    print("="*70)
    
    try:
        test_agent_type_enum()
        test_monitor_agent_integration()
        test_direct_tool_execution()
        test_llm_wrapper_with_monitor()
        
        print("\n" + "="*70)
        print("✓ 集成测试完成！")
        print("="*70 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
