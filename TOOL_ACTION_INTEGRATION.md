# Tool Action 集成文档

## 问题背景

Monitor Agent 执行工具操作（如隐藏、显示、放大摄像头）时，工具结果只存储在后端内存中，前端没有收到任何通知，导致页面无法更新。

## 解决方案

实现了一个完整的 **Tool Action 事件流**，使前端能够实时获知后端的工具执行结果并更新 UI。

## 架构流程

```
用户输入 (语音/文本)
    ↓
/chat 或 /audio 接口
    ↓
LLM 识别意图 → 触发 Monitor Agent
    ↓
Monitor Agent.inference_stream()
    ↓
执行工具调用
    ↓
**生成 tool_action 事件** (NEW)
    ↓
发送 SSE 流到前端
    ↓
前端 handleStream() 接收
    ↓
**处理 tool_action 事件** (NEW)
    ↓
调用 window.monitorControl 更新 UI
    ↓
摄像头显示/隐藏/缩放
```

## 代码修改详解

### 1. 后端：Monitor Agent (monitor_agent.py)

**修改位置**：`inference_stream()` 方法

**关键改动**：在工具执行后，生成 `tool_action` 事件并发送给前端

```python
# 执行工具
tool_result = self.tools.execute_tool(tool_name, tool_input)

# **关键：向前端发送工具执行结果**
tool_action_event = {
    "type": "tool_action",
    "tool_name": tool_name,
    "tool_input": tool_input,
    "tool_result": tool_result
}
yield json.dumps(tool_action_event, ensure_ascii=False)
```

**优势**：
- 后端工具执行结果直接流向前端
- 前端立即获知工具执行状态
- SSE 流保证实时性和可靠性

### 2. 前端：处理 Tool Action (app.js)

**修改位置**：`handleStream()` 函数和新增 `handleToolAction()` 函数

**关键改动**：添加 `tool_action` 事件处理

```javascript
} else if (data.type === 'tool_action') {
    // 处理Monitor Agent的工具执行结果
    console.log('Tool action received:', data);
    handleToolAction(data);
}
```

**新增函数**：

```javascript
function handleToolAction(toolAction) {
    const { tool_name, tool_input, tool_result } = toolAction;
    
    console.log(`Executing tool: ${tool_name}`, {input: tool_input, result: tool_result});
    
    // 更新监控器状态
    if (window.monitorControl) {
        if (tool_name === 'show_camera' && tool_input.camera_name) {
            window.monitorControl.showCamera(tool_input.camera_name);
        } else if (tool_name === 'hide_camera' && tool_input.camera_name) {
            window.monitorControl.hideCamera(tool_input.camera_name);
        } else if (tool_name === 'show_all_cameras') {
            window.monitorControl.showAllCameras();
        } else if (tool_name === 'hide_all_cameras') {
            window.monitorControl.hideAllCameras();
        } else if (tool_name === 'zoom_camera' && tool_input.camera_name) {
            window.monitorControl.zoomCamera(tool_input.camera_name);
        }
    }
}
```

**优势**：
- 集中处理所有工具动作
- 易于扩展支持新工具
- 清晰的控制流

### 3. 前端：Monitor Control API (monitor-control.js)

**修改位置**：新增 `window.monitorControl` 对象

**实现的方法**：

```javascript
window.monitorControl = {
    // 显示指定摄像头
    showCamera(cameraName) { ... },
    
    // 隐藏指定摄像头
    hideCamera(cameraName) { ... },
    
    // 显示所有摄像头
    showAllCameras() { ... },
    
    // 隐藏所有摄像头
    hideAllCameras() { ... },
    
    // 放大/缩放摄像头
    zoomCamera(cameraName) { ... },
    
    // 添加系统消息
    addMessage(message) { ... }
}
```

**优势**：
- 全局 API，易于前端调用
- 支持远程摄像头控制
- 集成了 3D 显示功能

## 支持的工具操作

### 1. show_camera
- **功能**：显示指定摄像头
- **输入**：`{"camera_name": "JinLiLite1"}`
- **前端响应**：`window.monitorControl.showCamera("JinLiLite1")`

### 2. hide_camera
- **功能**：隐藏指定摄像头
- **输入**：`{"camera_name": "ChiWen2"}`
- **前端响应**：`window.monitorControl.hideCamera("ChiWen2")`

### 3. show_all_cameras
- **功能**：显示所有摄像头
- **输入**：`{}`
- **前端响应**：`window.monitorControl.showAllCameras()`

### 4. hide_all_cameras
- **功能**：隐藏所有摄像头
- **输入**：`{}`
- **前端响应**：`window.monitorControl.hideAllCameras()`

### 5. zoom_camera
- **功能**：放大/缩放摄像头（在 3D 场景中显示）
- **输入**：`{"camera_name": "JinLiLite3"}`
- **前端响应**：`window.monitorControl.zoomCamera("JinLiLite3")`

### 6. list_cameras
- **功能**：列出指定平台的摄像头
- **输入**：`{"platform": "JinLiLite"}`
- **前端响应**：无直接 UI 更新（查询命令）

### 7. get_camera_status
- **功能**：获取指定摄像头的状态
- **输入**：`{"camera_name": "JinLiLite1"}`
- **前端响应**：无直接 UI 更新（查询命令）

## 数据流示例

### 用户说：「显示JinLiLite1摄像头」

**后端流程**：
```
1. User: "显示JinLiLite1摄像头"
2. Monitor Agent 识别意图
3. LLM 调用工具：show_camera(camera_name="JinLiLite1")
4. 工具执行：state.show_camera("JinLiLite1") → {status: "success", ...}
5. 生成事件：
   {
     "type": "tool_action",
     "tool_name": "show_camera",
     "tool_input": {"camera_name": "JinLiLite1"},
     "tool_result": {
       "status": "success",
       "message": "Camera JinLiLite1 is now visible",
       "camera": {...}
     }
   }
6. 发送 SSE：data: {...}
```

**前端流程**：
```
1. 接收 SSE 事件
2. 解析 JSON：data.type === 'tool_action'
3. 调用 handleToolAction(data)
4. 识别工具：tool_name === 'show_camera'
5. 调用 API：window.monitorControl.showCamera("JinLiLite1")
6. 更新 DOM：显示摄像头
7. 添加系统消息：[CAMERA] Showed camera: JinLiLite1
```

## 测试结果

✅ **后端测试**：所有 7 个工具都能正确生成 tool_action 事件
✅ **状态管理**：摄像头状态能正确同步（show/hide）
✅ **JSON 序列化**：事件能正确序列化和反序列化
✅ **前端 API**：window.monitorControl 对象包含所有必需的方法

## 故障排除

### 问题 1：摄像头没有显示/隐藏

**检查**：
1. 浏览器控制台是否有错误？
2. 是否收到 `tool_action` 事件？
3. `window.monitorControl` 是否已初始化？

**解决**：
1. 确保 monitor-control.js 已加载
2. 检查 console 日志中的 `[MonitorControl]` 消息
3. 验证 monitorManager 已初始化

### 问题 2：工具执行失败

**检查**：
1. LLM 是否能识别意图？
2. 工具输入是否正确？
3. 摄像头名称是否有效？

**解决**：
1. 查看 Monitor Agent 的日志
2. 检查 tool_result 中的 error 字段
3. 验证摄像头名称（JinLiLite1-3, ChiWen1-3）

## 扩展指南

### 添加新工具

1. 在 `monitor_tools.py` 中定义工具
2. 确保返回 `{status, action, data/error}` 格式
3. Monitor Agent 会自动发送 tool_action 事件
4. 在前端 `handleToolAction()` 中添加处理逻辑
5. 在 `window.monitorControl` 中添加对应方法

### 添加新事件类型

1. 在后端发送新的事件类型
2. 在前端 `handleStream()` 中添加 else if 条件
3. 实现相应的处理函数

## 相关文件

- 后端：`core/agents/monitor_agent.py` (inference_stream 方法)
- 前端：`static/app.js` (handleStream, handleToolAction 函数)
- 控制 API：`static/monitor-control.js` (window.monitorControl 对象)
- 状态管理：`core/agents/monitor_state.py`
- 工具定义：`core/agents/monitor_tools.py`

## 总结

Tool Action 集成解决了后端工具执行与前端 UI 更新的脱离问题。现在用户说一句话，系统就能实时反馈：

**「显示摄像头」→ 摄像头立即显示** ✨
