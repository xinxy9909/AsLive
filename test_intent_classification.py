#!/usr/bin/env python3
"""
LLM 意图识别和多 Agent 路由测试脚本
"""

import sys
from core.llm import LLMWrapper, AgentType, intent_classifier

def test_intent_classification():
    """测试意图识别功能"""
    print("=" * 60)
    print("测试：意图识别")
    print("=" * 60)
    
    test_queries = [
        "Python 如何读取 JSON 文件？",
        "今年 AI 领域有哪些重要进展？",
        "什么是机器学习？",
        "请帮我写一篇关于未来教育的文章",
        "你好，今天天气怎么样？",
    ]
    
    for query in test_queries:
        agent_type = intent_classifier.classify(query)
        print(f"\n用户: {query}")
        print(f"→ 选择 Agent: {agent_type.value}")


def test_llm_with_intent_classification():
    """测试启用意图识别的 LLM"""
    print("\n" + "=" * 60)
    print("测试：LLM 推理（启用意图识别）")
    print("=" * 60)
    
    llm = LLMWrapper(enable_intent_classification=True)
    
    test_query = "请解释什么是递归算法"
    print(f"\n用户: {test_query}")
    print(f"选择的 Agent: {llm.current_agent.value if hasattr(llm, 'current_agent') else 'unknown'}")
    
    # 注：实际使用时会流式生成结果
    # for chunk in llm.inference_stream(test_query):
    #     print(chunk, end="", flush=True)
    print("\n（实际运行会流式输出 LLM 生成的内容）")


def test_llm_without_intent_classification():
    """测试禁用意图识别的 LLM"""
    print("\n" + "=" * 60)
    print("测试：LLM 推理（禁用意图识别，使用默认 Agent）")
    print("=" * 60)
    
    llm = LLMWrapper(enable_intent_classification=False)
    print("\n意图识别已禁用，所有请求使用默认 Agent: ai-native")
    

def test_agent_selection():
    """测试 Agent 选择"""
    print("\n" + "=" * 60)
    print("测试：Agent 选择机制")
    print("=" * 60)
    
    llm = LLMWrapper(enable_intent_classification=True)
    
    test_cases = [
        ("怎样学习 Python 编程？", AgentType.CODE),
        ("最新的深度学习技术有哪些？", AgentType.SEARCH),
        ("解释什么是 API", AgentType.KNOWLEDGE),
        ("写一首关于春天的诗", AgentType.OPENAI),
    ]
    
    for query, expected_agent in test_cases:
        selected = llm.select_agent(query)
        print(f"\n查询: {query}")
        print(f"选择: {selected.value} (期望: {expected_agent.value})")


def main():
    """主函数"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   LLM 意图识别和多 Agent 路由功能测试                       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        # 运行测试
        test_intent_classification()
        test_llm_with_intent_classification()
        test_llm_without_intent_classification()
        test_agent_selection()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print("\n提示:")
        print("- 意图识别使用 AI-Native LLM 完成")
        print("- 可在 docs/LLM意图识别和多Agent路由.md 查看详细文档")
        print("- 通过环境变量 DEFAULT_AGENT 可设置默认 Agent")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
