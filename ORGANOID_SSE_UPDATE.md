# 类器官 Agent SSE 解析更新

## 更新内容

### 修改文件
- `core/agents/organoid_agent.py` - 更新 `_parse_sse()` 函数

### 更新说明

#### 之前的实现
```python
# 之前：简单地解析任何 JSON 数据
for raw_line in response.iter_lines(decode_unicode=True):
    if not raw_line or not raw_line.startswith("data:"):
        continue
    data_str = raw_line[len("data:"):].strip()
    event = json.loads(data_str)
    content = event.get("content") or ...
    if content:
        yield content
```

**问题**：
- ❌ 处理所有行，包括非 `event:message` 的事件
- ❌ 没有过滤消息类型，会输出所有内容（thinking、planning 等）
- ❌ 无法正确解析类器官 Agent 的实际响应格式

#### 现在的实现
```python
# 现在：正确处理 SSE 事件和消息类型过滤
for raw_line in response.iter_lines(decode_unicode=True):
    # 1. 解析 event: 字段
    if raw_line.startswith("event:"):
        current_event = raw_line[len("event:"):].strip()
        continue
    
    # 2. 解析 data: 字段
    if raw_line.startswith("data:"):
        data_str = raw_line[len("data:"):].strip()
        
        # 3. 只处理 message 事件
        if current_event == "message":
            event = json.loads(data_str)
            
            # 4. 只输出 type 为 ai 的消息
            if event.get("type") == "ai":
                content = event.get("data", "")
                if content:
                    yield content
```

**改进**：
- ✅ 正确处理 SSE 事件格式（event + data）
- ✅ 只处理 `event:message` 事件
- ✅ 只输出 `type: ai` 的消息
- ✅ 过滤掉 thinking、planning 等中间步骤
- ✅ 完整的日志记录

### 消息格式

类器官 Agent 返回的 SSE 格式：

```
event: message
data: {"type": "ai", "data": "实际的响应内容"}

event: message
data: {"type": "thinking", "data": "思考过程（会被过滤）"}

event: message
data: [DONE]
```

**我们只处理和输出**：
- `event: message` 事件
- `type: ai` 的消息
- `data` 字段中的内容

**会被过滤的**：
- 其他事件类型（heartbeat、error 等）
- 其他消息类型（thinking、planning、summary 等）
- 空消息

### 测试覆盖

新增测试脚本 `test_organoid_sse.py`，验证：

✅ **基础功能**
- 正确解析 SSE 格式
- 正确过滤 AI 类型消息
- 正确忽略其他类型消息

✅ **边界情况**
- 空 AI 消息被过滤
- 混合类型消息正确分离
- 非 message 事件被忽略

✅ **实际场景**
- 处理完整的多消息流
- 正确处理流结束标记 `[DONE]`

### 运行测试

```bash
python test_organoid_sse.py
```

输出：
```
✅ 所有测试通过！
```

### 使用示例

```python
from core.llm import LLMWrapper

# 创建 LLM 实例
llm = LLMWrapper(enable_intent_classification=False)

# 查询类器官问题
query = "帮我进行IPS心脏类器官的原代培养，样本数1，传代次数1"

# 流式输出（自动过滤 AI 类型的消息）
print("查询:", query)
print("\n响应:")
for chunk in llm.inference_stream(query):
    print(chunk, end="", flush=True)
print()
```

### 性能影响

- **解析性能**：无显著变化（仍为 O(n)）
- **内存占用**：不增加（使用流式处理）
- **延迟**：无增加（即时处理每一行）

### 日志输出

启用 DEBUG 日志可以看到详细的解析过程：

```
DEBUG: Received event: message
DEBUG: Yielding AI message: 我来帮您分析IPS...
DEBUG: Skipping non-AI message, type: thinking
```

### 向后兼容性

✅ 完全兼容现有 API
- LLMWrapper 接口不变
- OrganoidAgent 接口不变
- 只改进了内部 SSE 解析逻辑

---

**更新日期**: 2024-04-16  
**更新内容**: 修正类器官 Agent SSE 消息解析  
**测试状态**: ✅ 全部通过  
**兼容性**: ✅ 向后兼容
