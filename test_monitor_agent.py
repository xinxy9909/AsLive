#!/usr/bin/env python3
"""
Monitor Agent 测试脚本
"""

import sys
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 导入Monitor Agent
from core.agents.monitor_state import MonitorState
from core.agents.monitor_tools import MonitorTools
from core.agents.monitor_agent import MonitorAgent


def test_monitor_state():
    """测试Monitor状态管理"""
    print("\n" + "="*50)
    print("测试 1: Monitor State")
    print("="*50)
    
    state = MonitorState()
    
    # 测试获取所有摄像头
    all_cameras = state.get_all_cameras()
    print(f"\n✓ 获取所有摄像头: {len(all_cameras)} 个")
    for cam in all_cameras:
        print(f"  - {cam.name} ({cam.platform}): {cam.url}")
    
    # 测试按平台获取
    jinlilite_cams = state.get_cameras_by_platform("JinLiLite")
    print(f"\n✓ JinLiLite平台摄像头: {len(jinlilite_cams)} 个")
    for cam in jinlilite_cams:
        print(f"  - {cam.name}")
    
    chiwen_cams = state.get_cameras_by_platform("ChiWen")
    print(f"\n✓ ChiWen平台摄像头: {len(chiwen_cams)} 个")
    for cam in chiwen_cams:
        print(f"  - {cam.name}")
    
    # 测试隐藏/显示
    state.hide_camera("JinLiLite1")
    cam = state.get_camera("JinLiLite1")
    print(f"\n✓ 隐藏JinLiLite1后，visible={cam.visible}")
    
    state.show_camera("JinLiLite1")
    cam = state.get_camera("JinLiLite1")
    print(f"✓ 显示JinLiLite1后，visible={cam.visible}")
    
    # 测试放大
    state.zoom_camera("JinLiLite1", "fullscreen")
    cam = state.get_camera("JinLiLite1")
    print(f"✓ 放大JinLiLite1后，zoom_level={cam.zoom_level}")


def test_monitor_tools():
    """测试Monitor Tools"""
    print("\n" + "="*50)
    print("测试 2: Monitor Tools")
    print("="*50)
    
    state = MonitorState()
    tools = MonitorTools(state)
    
    # 测试list_cameras
    result = tools.list_cameras("JinLiLite")
    print(f"\n✓ list_cameras 结果:")
    print(f"  状态: {result['status']}")
    print(f"  消息: {result['data']['message']}")
    print(f"  摄像头数: {len(result['data']['cameras'])}")
    
    # 测试zoom_camera
    result = tools.zoom_camera("JinLiLite1", "fullscreen")
    print(f"\n✓ zoom_camera 结果:")
    print(f"  状态: {result['status']}")
    print(f"  消息: {result['data']['message']}")
    print(f"  URL: {result['data']['url']}")
    
    # 测试hide_camera
    result = tools.hide_camera("JinLiLite2")
    print(f"\n✓ hide_camera 结果:")
    print(f"  状态: {result['status']}")
    print(f"  消息: {result['data']['message']}")
    
    # 测试get_camera_status
    result = tools.get_camera_status("JinLiLite1")
    print(f"\n✓ get_camera_status 结果:")
    print(f"  状态: {result['status']}")
    print(f"  摄像头: {result['data']['camera']['name']}")
    print(f"  可见: {result['data']['camera']['visible']}")
    print(f"  放大级别: {result['data']['camera']['zoom_level']}")
    
    # 测试hide_all_cameras
    result = tools.hide_all_cameras("ChiWen")
    print(f"\n✓ hide_all_cameras 结果:")
    print(f"  状态: {result['status']}")
    print(f"  消息: {result['data']['message']}")
    print(f"  隐藏的摄像头: {result['data']['hidden_cameras']}")
    
    # 测试show_all_cameras
    result = tools.show_all_cameras("ChiWen")
    print(f"\n✓ show_all_cameras 结果:")
    print(f"  状态: {result['status']}")
    print(f"  消息: {result['data']['message']}")
    print(f"  显示的摄像头: {result['data']['shown_cameras']}")


def test_monitor_agent():
    """测试Monitor Agent"""
    print("\n" + "="*50)
    print("测试 3: Monitor Agent")
    print("="*50)
    
    agent = MonitorAgent()
    print("\n✓ Monitor Agent 初始化成功")
    
    # 测试工具定义
    tools = agent.tools.get_tools_definition()
    print(f"\n✓ 可用工具数: {len(tools)}")
    for tool in tools:
        print(f"  - {tool['function']['name']}: {tool['function']['description']}")
    
    # 测试推理流程（不实际调用LLM）
    print("\n✓ 测试 inference_stream（模拟环境中可能失败，这是正常的）")
    print("  注意：需要配置有效的 LLM_API_KEY 才能真正测试推理")


def test_tools_definition():
    """测试工具定义格式"""
    print("\n" + "="*50)
    print("测试 4: Tools Definition")
    print("="*50)
    
    state = MonitorState()
    tools = MonitorTools(state)
    tools_def = tools.get_tools_definition()
    
    print(f"\n✓ 工具定义数: {len(tools_def)}")
    
    for tool in tools_def:
        print(f"\n工具: {tool['function']['name']}")
        print(f"  描述: {tool['function']['description']}")
        params = tool['function']['parameters']['properties']
        print(f"  参数: {', '.join(params.keys())}")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Monitor Agent 综合测试")
    print("="*60)
    
    try:
        test_monitor_state()
        test_monitor_tools()
        test_monitor_agent()
        test_tools_definition()
        
        print("\n" + "="*60)
        print("✓ 所有测试完成！")
        print("="*60 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
