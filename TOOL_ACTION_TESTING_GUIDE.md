# Tool Action 功能测试指南

## 快速开始

### 前置条件

1. AsLive 项目已启动：`python api_server.py`
2. 浏览器打开 http://localhost:8000
3. 浏览器开发者控制台已打开（F12）

## 测试方案 1：文本命令测试

### 场景 1.1：显示单个摄像头

**操作步骤**：
1. 在文本输入框输入：`显示JinLiLite1摄像头`
2. 点击 Send 按钮
3. 观察结果

**预期结果**：
- 控制台显示：`Tool action received: {type: "tool_action", tool_name: "show_camera", ...}`
- 摄像头区域显示 JinLiLite1 摄像头
- 聊天记录中出现：`[CAMERA] Showed camera: JinLiLite1`

**检查点**：
```javascript
// 在浏览器控制台执行
console.log('Camera visible:', window.monitorManager?.activeMonitors?.has('JinLiLite1'))
```

### 场景 1.2：隐藏摄像头

**操作步骤**：
1. 输入：`隐藏JinLiLite1摄像头`
2. 点击 Send

**预期结果**：
- JinLiLite1 摄像头消失
- 控制台显示：`Tool action received: {tool_name: "hide_camera", ...}`
- 聊天记录显示：`[CAMERA] Hidden camera: JinLiLite1`

### 场景 1.3：显示所有摄像头

**操作步骤**：
1. 输入：`显示所有摄像头`
2. 点击 Send

**预期结果**：
- 6 个摄像头全部显示
- 分别为：JinLiLite1-3, ChiWen1-3

### 场景 1.4：隐藏所有摄像头

**操作步骤**：
1. 输入：`隐藏所有摄像头`
2. 点击 Send

**预期结果**：
- 所有摄像头消失
- 只有聊天区域可见

### 场景 1.5：放大摄像头

**操作步骤**：
1. 输入：`放大ChiWen2摄像头`（或 `看ChiWen2`、`全屏ChiWen2` 等同义表达）
2. 点击 Send

**预期结果**：
- ChiWen2 摄像头显示
- 在 3D 场景中显示该摄像头
- 聊天记录显示：`[CAMERA] Zoomed camera: ChiWen2`

## 测试方案 2：组合命令测试

### 场景 2.1：序列控制

**操作步骤**：
1. 依次输入以下命令：
   ```
   显示所有摄像头
   隐藏JinLiLite2
   放大ChiWen1
   ```

**预期结果**：
- 每个命令执行后，摄像头显示状态相应改变
- 没有错误或卡顿
- 流畅的用户体验

### 场景 2.2：列表查询

**操作步骤**：
1. 输入：`有哪些摄像头`

**预期结果**：
- 后端执行 `list_cameras` 工具（可在后台看到工具执行）
- AI 返回摄像头列表
- 无 UI 改变（这是查询工具，不改变显示状态）

## 测试方案 3：浏览器控制台验证

### 检查 Tool Action 事件接收

```javascript
// 在控制台执行，可以看到所有接收到的 tool_action 事件
window._toolActions = [];
const originalLog = console.log;
console.log = function(...args) {
    if (args[0] === 'Tool action received:') {
        window._toolActions.push(args[1]);
    }
    originalLog.apply(console, args);
};

// 现在执行命令，然后查询
console.log(window._toolActions);
```

### 检查摄像头状态

```javascript
// 查看当前可见的摄像头
const activeMonitors = Array.from(window.monitorManager?.activeMonitors || []);
console.log('Active monitors:', activeMonitors);

// 查看所有摄像头配置
console.log('All cameras:', window.monitorManager?.monitors);

// 查看特定摄像头的可见性
console.log('JinLiLite1 visible:', window.monitorManager?.activeMonitors?.has('JinLiLite1'));
```

### 手动调用控制 API

```javascript
// 这些都是可以直接调用的
window.monitorControl.showCamera('JinLiLite1');
window.monitorControl.hideCamera('JinLiLite2');
window.monitorControl.showAllCameras();
window.monitorControl.hideAllCameras();
window.monitorControl.zoomCamera('ChiWen1');
```

## 测试方案 4：网络监控

### 检查 SSE 流数据

1. 打开浏览器开发者工具 → Network 标签
2. 输入命令并发送
3. 找到 `/chat` 请求
4. 选择 Response 标签，查看 SSE 事件流

**预期见到的事件类型**：
```
data: {"type": "start", ...}
data: {"type": "text", "content": "..."}
data: {"type": "tool_action", "tool_name": "show_camera", ...}
data: {"type": "text", "content": "..."}
data: {"type": "audio", ...}
data: {"type": "end", ...}
```

### 检查 tool_action 事件格式

```
data: {"type":"tool_action","tool_name":"show_camera","tool_input":{"camera_name":"JinLiLite1"},"tool_result":{"status":"success","message":"Camera JinLiLite1 is now visible","camera":{...}}}
```

## 测试方案 5：错误恢复测试

### 场景 5.1：无效的摄像头名称

**操作步骤**：
1. 输入：`显示InvalidCamera摄像头`

**预期结果**：
- 后端会返回错误信息
- tool_result 中 status 为 "error"
- AI 告知用户摄像头不存在
- 系统不会崩溃

### 场景 5.2：快速连续命令

**操作步骤**：
1. 快速输入多个命令（不等待响应）

**预期结果**：
- 系统处理所有命令（可能会打断前面的流）
- 最终状态与最后一个命令对应
- 没有错误或重复显示

## 测试检查清单

### 后端检查

- [ ] Monitor Agent 能识别意图
- [ ] LLM 能正确调用摄像头工具
- [ ] 工具执行返回正确的结果
- [ ] tool_action 事件被正确生成和序列化
- [ ] SSE 流正常发送到前端
- [ ] 没有 Python 错误或异常

### 前端检查

- [ ] handleStream() 能识别 tool_action 事件
- [ ] JSON 解析正确
- [ ] handleToolAction() 被调用
- [ ] window.monitorControl 对象存在
- [ ] 摄像头显示/隐藏操作执行
- [ ] DOM 元素正确更新
- [ ] 聊天消息正确显示

### 集成检查

- [ ] 用户命令能完整地流向摄像头显示
- [ ] 没有延迟或卡顿
- [ ] 用户体验流畅
- [ ] 多个摄像头操作不冲突
- [ ] 系统稳定性好

## 常见问题排查

### Q1：摄像头不显示

**检查步骤**：
1. 浏览器控制台是否有 JavaScript 错误？
2. `window.monitorControl` 是否已定义？
3. `window.monitorManager` 是否已初始化？
4. Monitor 容器是否在 DOM 中？

**调试代码**：
```javascript
console.log('monitorControl:', window.monitorControl);
console.log('monitorManager:', window.monitorManager);
console.log('Container:', document.getElementById('monitor-container'));
```

### Q2：没有收到 tool_action 事件

**检查步骤**：
1. 网络请求是否成功（Network 标签）？
2. SSE 流是否正常（Response 显示 data:）？
3. 后端是否正确发送了事件？
4. JSON 格式是否正确？

**调试代码**：
```javascript
// 在 handleStream 中添加日志
console.log('Raw chunk:', chunk);
console.log('Lines:', lines);
```

### Q3：LLM 不调用工具

**检查步骤**：
1. 用户输入是否清晰明确？
2. 摄像头名称是否正确？
3. LLM API 密钥是否有效？
4. Monitor Agent 系统提示词是否正确？

**调试命令**：
```python
# 后端测试
from core.agents.monitor_agent import MonitorAgent
agent = MonitorAgent()
for chunk in agent.inference_stream([{"role": "user", "content": "显示JinLiLite1"}]):
    print(chunk)
```

## 性能测试

### 响应时间测试

**测试方法**：
1. 在 handleToolAction 开始和结束处添加时间戳
2. 测量事件处理耗时

**预期结果**：
- 事件接收到 DOM 更新：< 50ms
- 用户感知延迟：< 1 秒

### 并发测试

**测试方法**：
1. 快速发送多个命令
2. 监控内存和 CPU 使用
3. 检查是否有内存泄漏

**预期结果**：
- 内存使用稳定
- 没有性能下降
- 命令执行无重复或丢失

## 文档参考

- 完整说明：[TOOL_ACTION_INTEGRATION.md](TOOL_ACTION_INTEGRATION.md)
- 解决方案总结：[TOOL_ACTION_SOLUTION_SUMMARY.md](TOOL_ACTION_SOLUTION_SUMMARY.md)
- Monitor Agent 文档：[MONITOR_AGENT_README.md](MONITOR_AGENT_README.md)

## 反馈和问题

如果遇到问题或发现 bug：
1. 记录问题描述和复现步骤
2. 提供浏览器控制台错误信息
3. 提供网络请求的 SSE 流内容
4. 提供后端日志输出

---

**测试愉快！** 🎉
