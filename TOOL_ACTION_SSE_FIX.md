# Tool Action SSE 事件传输修复

## 问题描述

Monitor Agent 的 tool_action 事件没有被正确发送到前端，前端接收到的是被包装为文本的 JSON 字符串。

### 症状

前端收到的 SSE 消息：
```
data: {"type": "text", "content": "{\"type\": \"tool_action\", \"tool_name\": \"show_camera\", ...}"}
```

前端期望接收：
```
data: {"type": "tool_action", "tool_name": "show_camera", ...}
```

### 根本原因

在 `api_server.py` 的 `process_streaming()` 函数中，所有来自 LLM（包括 Monitor Agent）的输出都被当作普通文本流处理：

```python
for chunk in llm.inference_stream_chat(context_messages):
    full_response += chunk
    # ❌ 直接将所有 chunk 包装成 text 类型
    yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
```

Monitor Agent 的 `inference_stream()` 返回：
1. 普通对话文本
2. **tool_action JSON 事件**（新增）

但第2种被错误地当作了第1种处理。

## 解决方案

在 `process_streaming()` 中添加事件类型检测：

```python
for chunk in llm.inference_stream_chat(context_messages):
    # **[NEW] 检测是否为 tool_action 事件**
    try:
        potential_event = json.loads(chunk)
        if isinstance(potential_event, dict) and potential_event.get('type') == 'tool_action':
            # 这是一个 tool_action 事件，直接转发给前端
            print(f"[SSE] Tool action event detected: {potential_event.get('tool_name')}")
            yield f"data: {json.dumps(potential_event)}\n\n"
            continue
    except (json.JSONDecodeError, ValueError):
        # 不是 JSON，当作普通文本处理
        pass

    full_response += chunk
    # 普通文本，包装成 text 类型
    yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
```

## 修改详解

### 文件：api_server.py

**函数**：`process_streaming()`

**位置**：约 135-165 行

**变更内容**：在处理每个 chunk 时，添加 JSON 解析和事件类型检测

**关键逻辑**：
1. 尝试将 chunk 解析为 JSON
2. 如果是有效的 tool_action 事件，直接转发（不包装）
3. 否则当作文本处理（包装为 text 类型）

### 影响范围

✅ Monitor Agent 的 tool_action 事件现在能正确传输
✅ 普通文本响应不受影响
✅ 向后兼容（其他 Agent 的行为不变）
✅ 性能影响最小（JSON 尝试解析只在 chunk 层级）

## 完整的SSE流程

### 修复前

```
Monitor Agent.inference_stream()
    ↓
yield: {"type": "tool_action", ...}  (JSON string)
    ↓
process_streaming() 接收
    ↓
❌ 当作普通文本，包装为 text
    ↓
前端收到: {"type": "text", "content": "{\"type\": \"tool_action\", ...}"}
    ↓
❌ 前端解析 content，变成 JSON 字符串而非对象
    ↓
handleToolAction() 无法识别
```

### 修复后

```
Monitor Agent.inference_stream()
    ↓
yield: {"type": "tool_action", ...}  (JSON string)
    ↓
process_streaming() 接收
    ↓
✓ 检测到是 JSON 且 type == 'tool_action'
    ↓
✓ 直接转发，不包装
    ↓
前端收到: {"type": "tool_action", "tool_name": "show_camera", ...}
    ↓
✓ 前端识别为 tool_action
    ↓
✓ handleToolAction() 正确路由
    ↓
✓ window.monitorControl.showCamera() 执行
```

## 测试验证

### 测试场景

**输入**：用户说「显示ChiWen1摄像头」

**预期 SSE 流**：
```
data: {"type": "start", "session_id": "..."}

data: {"type": "tool_action", "tool_name": "show_camera", "tool_input": {"camera_name": "ChiWen1"}, "tool_result": {...}}

data: {"type": "text", "content": "已为您显示ChiWen1摄像头。"}

data: {"type": "audio", "url": "/outputs/...", "text": "..."}

data: {"type": "end", ...}
```

**验证方法**：
1. 打开浏览器 Network 标签
2. 发送文本命令
3. 查看 `/chat` 请求的 Response
4. 确认 tool_action 事件格式正确（无 "text" 包装）

### 浏览器控制台验证

```javascript
// 监听 tool_action 事件
const originalLog = console.log;
window._toolActions = [];
console.log = function(...args) {
    if (args[0]?.includes('Tool action received')) {
        window._toolActions.push(args[1]);
        console.log('✓ Captured tool_action:', args[1]);
    }
    originalLog.apply(console, args);
};

// 发送命令后查询
console.log('Received tool actions:', window._toolActions);
```

## 性能影响

- **JSON 解析尝试**：每个 chunk 一次（< 1ms）
- **条件检查**：O(1) 操作
- **总体影响**：可忽略不计

## 安全性

✅ JSON 解析异常被捕获，不会导致崩溃
✅ 只检测 type == 'tool_action'，其他事件不受影响
✅ 不改变任何安全边界

## 相关文件

- 修改文件：`api_server.py` (process_streaming 函数)
- 相关代码：`core/agents/monitor_agent.py` (inference_stream 方法)
- 前端处理：`static/app.js` (handleStream, handleToolAction 函数)

## Git 提交

```
108729f fix: correctly handle tool_action events in process_streaming
```

## 现在的工作流程

用户命令 → Monitor Agent 识别 → 执行工具 → 生成 tool_action 事件 → **✓ 正确传输到前端** → 前端处理 → UI 更新

**用户说「显示摄像头」→ 摄像头立即显示** ✨

## 总结

这个修复确保了 Monitor Agent 的 tool_action 事件能够正确地从后端流向前端，完整实现了整个工具执行→UI 更新的闭环。

核心改动非常简单：**在转发 SSE 事件前，检测是否为 tool_action 事件，如果是则直接转发，否则包装为 text 类型**。

这保证了：
- ✅ tool_action 事件格式正确
- ✅ 前端能正确识别和处理
- ✅ 不影响其他功能
- ✅ 最小化代码改动（只需 13 行）
