#!/usr/bin/env python3
"""
类器官 Agent SSE 解析测试脚本
"""

import json
from io import StringIO
from unittest.mock import Mock, patch


def test_organoid_sse_parsing():
    """测试类器官 Agent 的 SSE 解析"""
    
    print("=" * 70)
    print("测试：类器官 Agent SSE 解析")
    print("=" * 70)
    
    # 模拟 SSE 响应数据
    sse_response = """event: message
data: {"type": "ai", "content": "我来帮您分析IPS"}
event: message
data: {"type": "thinking", "data": "思考过程..."}
event: message
data: {"type": "ai", "content": "心脏类器官的"}
event: message
data: {"type": "ai", "content": "原代培养..."}
event: message
data: [DONE]
"""
    
    print("\n模拟的 SSE 响应数据:")
    print("-" * 70)
    print(sse_response)
    print("-" * 70)
    
    # 导入 organoid_agent 的 _parse_sse 函数
    from core.agents.organoid_agent import _parse_sse
    
    # 模拟 requests.Response 对象
    mock_response = Mock()
    mock_response.iter_lines = Mock(return_value=sse_response.strip().split('\n'))
    
    # 测试解析
    print("\n解析结果:")
    print("-" * 70)
    
    collected_content = []
    for content in _parse_sse(mock_response):
        print(f"✓ {content}")
        collected_content.append(content)
    
    print("-" * 70)
    
    # 验证结果
    expected = ["我来帮您分析IPS", "心脏类器官的", "原代培养..."]
    actual = collected_content
    
    print(f"\n期望结果: {expected}")
    print(f"实际结果: {actual}")
    
    if actual == expected:
        print("\n✅ 测试通过！正确地过滤了非 AI 类型的消息")
    else:
        print("\n❌ 测试失败！")
        return False
    
    return True


def test_edge_cases():
    """测试边界情况"""
    
    print("\n" + "=" * 70)
    print("测试：边界情况")
    print("=" * 70)
    
    from core.agents.organoid_agent import _parse_sse
    
    # 测试情况 1: 空消息
    print("\n[1] 测试空 AI 消息...")
    sse_response = """event: message
data: {"type": "ai", "content": ""}
event: message
data: [DONE]
"""
    
    mock_response = Mock()
    mock_response.iter_lines = Mock(return_value=sse_response.strip().split('\n'))
    
    result = list(_parse_sse(mock_response))
    if len(result) == 0:
        print("✅ 正确过滤了空消息")
    else:
        print("❌ 错误：应该过滤空消息")
        return False
    
    # 测试情况 2: 混合类型消息
    print("\n[2] 测试混合类型消息...")
    sse_response = """event: message
data: {"type": "thinking", "data": "thinking1"}
event: message
data: {"type": "ai", "content": "response1"}
event: message
data: {"type": "planning", "data": "planning1"}
event: message
data: {"type": "ai", "content": "response2"}
event: message
data: [DONE]
"""
    
    mock_response = Mock()
    mock_response.iter_lines = Mock(return_value=sse_response.strip().split('\n'))
    
    result = list(_parse_sse(mock_response))
    expected = ["response1", "response2"]
    
    if result == expected:
        print(f"✅ 正确过滤了混合消息：{result}")
    else:
        print(f"❌ 过滤失败。期望: {expected}, 实际: {result}")
        return False
    
    # 测试情况 3: 非 message 事件
    print("\n[3] 测试非 message 事件...")
    sse_response = """event: heartbeat
data: {"type": "ai", "content": "should_be_ignored"}
event: message
data: {"type": "ai", "content": "should_be_included"}
event: message
data: [DONE]
"""
    
    mock_response = Mock()
    mock_response.iter_lines = Mock(return_value=sse_response.strip().split('\n'))
    
    result = list(_parse_sse(mock_response))
    expected = ["should_be_included"]
    
    if result == expected:
        print(f"✅ 正确过滤了非 message 事件：{result}")
    else:
        print(f"❌ 过滤失败。期望: {expected}, 实际: {result}")
        return False
    
    return True


if __name__ == "__main__":
    try:
        success = test_organoid_sse_parsing()
        if success:
            success = test_edge_cases()
        
        if success:
            print("\n" + "=" * 70)
            print("✅ 所有测试通过！")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("❌ 部分测试失败")
            print("=" * 70)
            exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
