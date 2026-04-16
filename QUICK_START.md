# LLM 意图识别快速开始指南

## 3 分钟快速上手

### 1. 基础使用

```python
from core.llm import LLMWrapper

# 创建 LLM 实例（默认启用意图识别）
llm = LLMWrapper()

# 简单查询
text = "如何用 Python 读取 CSV 文件？"
result = llm.inference(text)  # 返回完整结果
print(result)
```

### 2. 流式输出

```python
# 流式输出更快看到结果
for chunk in llm.inference_stream("解释什么是 REST API"):
    print(chunk, end="", flush=True)
```

### 3. 多轮对话

```python
messages = [
    {"role": "user", "content": "Python 中什么是装饰器？"},
    {"role": "assistant", "content": "装饰器是..."},
    {"role": "user", "content": "请给我一个实际的例子"},
]

for chunk in llm.inference_stream_chat(messages):
    print(chunk, end="", flush=True)
```

## 核心概念

### Agent 类型

系统会根据用户问题自动选择合适的 Agent：

| Agent | 场景 | 例子 |
|-------|------|------|
| **ai-native** | 通用对话 | 你好，今天天气怎么样？ |
| **code** | 编程问题 | 如何在 Python 中读取文件？ |
| **search** | 最新信息 | 2024 年 AI 有什么进展？ |
| **knowledge** | 知识讲解 | 什么是机器学习？ |
| **openai** | 创意任务 | 写一篇关于未来的科幻故事 |

### 工作原理

```
用户输入
    ↓
[意图识别] 使用 LLM 分析意图
    ↓
自动选择最合适的 Agent
    ↓
执行相应的 Agent
    ↓
返回结果
```

## 高级用法

### 禁用意图识别

如果只想使用默认 Agent，可以禁用意图识别：

```python
llm = LLMWrapper(enable_intent_classification=False)

# 所有请求都使用 DEFAULT_AGENT（默认为 ai-native）
```

### 在多轮对话中禁用意图识别

```python
llm.inference_stream_chat(
    messages,
    use_intent_classification=False  # 禁用意图识别
)
```

### 查看当前选择的 Agent

```python
agent = llm.select_agent("写一个 Python 程序")
print(f"选择的 Agent: {agent.value}")  # 输出: code
```

### 手动指定 Agent

虽然系统会自动选择，但你也可以查看选择过程：

```python
from core.llm import intent_classifier, AgentType

# 直接使用分类器
agent = intent_classifier.classify("Python 编程问题")
print(agent.value)  # 输出: code
```

## 环境配置

### 最小化配置（使用 AI-Native）

```bash
# .env 文件
LABILLION_BASE_URL=https://staging.automation.labillion.cn
LABILLION_PLATFORM_ID=<你的平台ID>
LABILLION_USERNAME=<你的用户名>
LABILLION_PASSWORD=<你的密码>
LABILLION_TENANT_ID=<你的租户ID>
```

### 完整配置（支持所有 Agent）

```bash
# .env 文件

# Labillion AI-Native 配置
LABILLION_BASE_URL=https://staging.automation.labillion.cn
LABILLION_PLATFORM_ID=<平台ID>
LABILLION_USERNAME=<用户名>
LABILLION_PASSWORD=<密码>
LABILLION_TENANT_ID=<租户ID>

# OpenAI 配置（可选）
OPENAI_API_KEY=sk-<你的API Key>
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# 默认 Agent 选择
DEFAULT_AGENT=ai-native
```

## 实际案例

### 场景 1: 代码帮助

```python
llm = LLMWrapper()

query = "怎样在 Python 中处理 JSON 数据？"
print("用户: " + query)
print("\n助手:")
for chunk in llm.inference_stream(query):
    print(chunk, end="", flush=True)

# 输出:
# 用户: 怎样在 Python 中处理 JSON 数据？
# 助手: [使用 Code Agent 回答]
```

### 场景 2: 信息查询

```python
query = "最近的深度学习研究进展有哪些？"
print("用户: " + query)
print("\n助手:")
for chunk in llm.inference_stream(query):
    print(chunk, end="", flush=True)

# 输出:
# 用户: 最近的深度学习研究进展有哪些？
# 助手: [使用 Search Agent 回答，强调最新信息]
```

### 场景 3: 多轮对话

```python
llm = LLMWrapper()

# 第一轮
messages = [{"role": "user", "content": "什么是云计算？"}]
print("用户: 什么是云计算？")
print("\n助手:")
response = llm.inference_stream_chat(messages)
assistant_reply = "".join(response)
messages.append({"role": "assistant", "content": assistant_reply})
print(assistant_reply)

# 第二轮
messages.append({"role": "user", "content": "给我举个具体的例子"})
print("\n用户: 给我举个具体的例子")
print("\n助手:")
response = llm.inference_stream_chat(messages)
for chunk in response:
    print(chunk, end="", flush=True)
```

## 故障排查

### 问题: 意图识别失败

**症状**: 所有问题都返回相同的回答

**解决**:
1. 检查 Labillion 连接是否正常
2. 查看日志信息: `logger.info()` 输出
3. 尝试禁用意图识别看是否是意图识别的问题

```python
llm = LLMWrapper(enable_intent_classification=False)
```

### 问题: OpenAI Agent 无法使用

**症状**: 收到 API Key 错误

**解决**:
1. 确认已配置 `OPENAI_API_KEY` 环境变量
2. 确认 API Key 有效且未过期
3. 检查 API 额度是否充足

未配置 API Key 时，系统会自动回退到 AI-Native。

### 问题: 响应变慢

**原因**: 意图识别需要额外的 LLM 调用

**解决**:
1. 禁用意图识别（只使用默认 Agent）
2. 后续可加入缓存机制加速

```python
llm = LLMWrapper(enable_intent_classification=False)
```

## 获取帮助

- 📖 详细文档: 查看 `docs/LLM意图识别和多Agent路由.md`
- 🧪 测试脚本: 运行 `python test_intent_classification.py`
- 📝 更新日志: 查看 `CHANGELOG.md`
- 🐛 问题报告: 查看日志输出的错误信息

## 下一步

✅ 基础功能完整  
🚀 建议尝试的方向:
1. 集成真实搜索引擎 API
2. 添加意图识别缓存
3. 集成知识库系统
4. 支持更多 LLM 模型（Claude、Gemini 等）

---

**更新日期**: 2024-04-16  
**版本**: 1.0
