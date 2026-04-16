# 类器官 Agent 使用快速指南

## 简介

类器官 Agent 是一个多模态推理系统，可以处理生物医学领域的复杂问题。

## 基本使用

### 1. 直接使用 OrganoidAgent

```python
from core.agents import OrganoidAgent

# 创建 Agent 实例
agent = OrganoidAgent()

# 单条消息推理
messages = [{"role": "user", "content": "帮我进行IPS心脏类器官的原代培养，样本数1，传代次数1"}]

# 流式输出
print("AI 响应:")
for chunk in agent.inference_stream(messages):
    print(chunk, end="", flush=True)
print()
```

### 2. 通过 LLMWrapper 使用

```python
from core.llm import LLMWrapper

# 创建 LLM（禁用意图识别，直接使用默认 Agent）
llm = LLMWrapper(enable_intent_classification=False)

# 或启用意图识别，自动选择 Agent
llm = LLMWrapper(enable_intent_classification=True)

# 流式推理
query = "帮我进行IPS心脏类器官的原代培养，样本数1，传代次数1"
for chunk in llm.inference_stream(query):
    print(chunk, end="", flush=True)
```

### 3. 多轮对话

```python
from core.llm import LLMWrapper

llm = LLMWrapper()

messages = [
    {"role": "user", "content": "IPS心脏类器官有什么优势？"},
    {"role": "assistant", "content": "...之前的响应..."},
    {"role": "user", "content": "如何进行原代培养？"},
]

# 多轮对话会自动选择最合适的 Agent
for chunk in llm.inference_stream_chat(messages):
    print(chunk, end="", flush=True)
```

## 配置

### 环境变量

```bash
# 类器官 Agent 配置
ORGANOID_BASE_URL=http://192.168.1.97:2026
ORGANOID_MODEL=qwen-plus
ORGANOID_THINKING_ENABLED=true
ORGANOID_CONFIG_NAME=mega_agent

# 默认 Agent 选择
DEFAULT_AGENT=ai-native  # 或 organoid
```

### 配置说明

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ORGANOID_BASE_URL` | `http://192.168.1.97:2026` | 类器官服务地址 |
| `ORGANOID_MODEL` | `qwen-plus` | 使用的模型 |
| `ORGANOID_THINKING_ENABLED` | `true` | 是否启用思考模式 |
| `ORGANOID_CONFIG_NAME` | `mega_agent` | 配置名称 |
| `DEFAULT_AGENT` | `ai-native` | 默认使用的 Agent |

## 消息格式

### 输入格式

```python
messages = [
    {
        "role": "user",        # 角色：user 或 assistant
        "content": "问题内容"  # 消息内容
    }
]
```

### 输出格式

类器官 Agent 返回的内容是经过过滤的 AI 消息，只包含最终响应，不包括：
- 思考过程 (thinking)
- 计划步骤 (planning)
- 中间摘要 (summary)

## 常见用例

### 用例 1: 类器官培养指导

```python
query = "帮我进行IPS心脏类器官的原代培养，样本数1，传代次数1"

for chunk in agent.inference_stream([{"role": "user", "content": query}]):
    print(chunk, end="", flush=True)
```

**预期输出**：
- 原代培养的详细步骤
- 培养条件和参数
- 注意事项

### 用例 2: 分化协议咨询

```python
query = "如何从iPSC诱导分化为心肌细胞？"

for chunk in agent.inference_stream([{"role": "user", "content": query}]):
    print(chunk, end="", flush=True)
```

**预期输出**：
- 分化步骤
- 细胞因子和浓度
- 时间安排

### 用例 3: 故障排除

```python
query = "类器官培养过程中出现了细菌污染，应该怎么处理？"

for chunk in agent.inference_stream([{"role": "user", "content": query}]):
    print(chunk, end="", flush=True)
```

**预期输出**：
- 污染原因分析
- 处理方案
- 预防措施

## SSE 消息过滤

类器官 Agent 的响应包括多种消息类型：

```
event: message
data: {"type": "thinking", "data": "...思考过程..."}  ← 被过滤

event: message
data: {"type": "ai", "data": "...实际响应..."}  ← 输出

event: message
data: {"type": "planning", "data": "...计划..."}  ← 被过滤
```

**系统会自动**：
- ✅ 只输出 `type: ai` 的消息
- ✅ 忽略思考、计划等中间步骤
- ✅ 提供清晰的最终响应

## 性能和延迟

| 指标 | 值 |
|------|-----|
| 首字节延迟 | ~100-500ms |
| 流式推理速度 | 实时 |
| 请求超时 | 60 秒 |
| 最大响应长度 | 无限制 |

## 错误处理

### 网络错误

```python
try:
    for chunk in agent.inference_stream(messages):
        print(chunk, end="", flush=True)
except requests.exceptions.ConnectionError:
    print("错误：无法连接到类器官服务")
except requests.exceptions.Timeout:
    print("错误：请求超时")
```

### 响应错误

```python
try:
    for chunk in agent.inference_stream(messages):
        print(chunk, end="", flush=True)
except Exception as e:
    print(f"错误：{e}")
```

## 日志和调试

### 启用详细日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# 现在会输出详细的日志
agent = OrganoidAgent()
for chunk in agent.inference_stream(messages):
    print(chunk, end="", flush=True)
```

### 日志输出示例

```
DEBUG: Organoid: Processing query: 帮我进行IPS心脏类器官...
DEBUG: Organoid: Submitting chat to http://192.168.1.97:2026/api/chat/submit
DEBUG: Organoid: Chat submitted with thread_id: abc-123-def
DEBUG: Organoid: Resuming chat from http://192.168.1.97:2026/api/chat/resume/abc-123-def?offset=0
DEBUG: Received event: message
DEBUG: Yielding AI message: 我来为您介绍IPS心脏类器官的原代...
```

## 故障排查

### 问题 1: 无响应

**症状**：Agent 没有返回任何内容

**检查清单**：
- [ ] 确认 ORGANOID_BASE_URL 配置正确
- [ ] 确认类器官服务正在运行
- [ ] 查看日志是否有错误

### 问题 2: 部分响应

**症状**：响应被中断或不完整

**检查清单**：
- [ ] 确认请求超时时间足够（60 秒）
- [ ] 查看网络连接状态
- [ ] 检查日志中的错误信息

### 问题 3: 非预期内容

**症状**：输出包含思考过程或其他中间步骤

**检查清单**：
- [ ] 确认使用的是最新版本的 organoid_agent.py
- [ ] 查看 SSE 消息类型是否正确为 "ai"

## 最佳实践

### 1. 使用流式推理

```python
# ✅ 推荐：立即看到结果
for chunk in agent.inference_stream(messages):
    print(chunk, end="", flush=True)

# ❌ 不推荐：等待完整响应
result = agent.inference(messages)
print(result)
```

### 2. 处理异常

```python
# ✅ 推荐
try:
    for chunk in agent.inference_stream(messages):
        print(chunk, end="", flush=True)
except Exception as e:
    logger.error(f"推理失败: {e}")

# ❌ 不推荐：无错误处理
for chunk in agent.inference_stream(messages):
    print(chunk, end="")
```

### 3. 启用日志

```python
# ✅ 推荐：在生产环境中启用日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 相关文件

- `core/agents/organoid_agent.py` - 实现文件
- `core/agents/base_agent.py` - 基类
- `test_organoid_sse.py` - 测试脚本
- `ORGANOID_SSE_UPDATE.md` - 技术详情

---

**最后更新**: 2024-04-16  
**版本**: 1.0
