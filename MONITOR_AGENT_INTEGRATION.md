# Monitor Agent 集成完成

## 概述

Monitor Agent 已成功集成到 AsLive 项目中，通过 LLM 意图识别自动路由到 Monitor Agent 处理视频监控相关的用户请求。

## 实现架构

### 1. 核心模块

#### 1.1 `core/agents/monitor_state.py`
- **功能**: 摄像头状态管理
- **主要类**:
  - `Camera`: 摄像头数据模型
  - `MonitorState`: 监控系统状态管理器
- **功能**:
  - 初始化和管理所有摄像头
  - 实现隐藏/显示/放大操作
  - 维护摄像头的状态（可见性、放大级别等）

#### 1.2 `core/agents/monitor_tools.py`
- **功能**: 定义 Monitor Agent 的所有可用工具
- **主要类**: `MonitorTools`
- **提供的工具**:
  1. `list_cameras` - 列出指定平台的所有摄像头
  2. `zoom_camera` - 放大指定摄像头
  3. `hide_camera` - 隐藏指定摄像头
  4. `hide_all_cameras` - 隐藏整个平台的所有摄像头
  5. `show_camera` - 显示隐藏的摄像头
  6. `show_all_cameras` - 显示所有摄像头
  7. `get_camera_status` - 查询摄像头状态

#### 1.3 `core/agents/monitor_agent.py`
- **功能**: Monitor Agent 核心实现
- **主要类**: `MonitorAgent`
- **继承**: `BaseAgent`
- **特性**:
  - 与 LLM 交互，支持工具调用
  - 循环执行直到完成（无更多工具调用）
  - 返回用户友好的操作结果

### 2. LLM 集成

#### `core/llm.py` 更新
- **新增 Agent 类型**: `AgentType.MONITOR`
- **更新意图描述**: 添加了"视频监控管理"意图
- **自动路由**: 当用户提出监控相关请求时，自动路由到 Monitor Agent
- **实例缓存**: Monitor Agent 实例与其他 Agent 一起缓存

### 3. 无需新增 API 接口

Monitor Agent 完全通过以下现有接口处理：
- `POST /chat` - 文本聊天接口
- `POST /audio` - 语音聊天接口

LLM Wrapper 自动识别意图并路由到相应的 Agent。

## 摄像头配置

### JinLiLite 平台
```
- JinLiLite1: https://monitor.data.labillion.cn/live/0f47c97f-8098-4f32-a34a-7eb8ea70cb26_1080p.m3u8
- JinLiLite2: https://monitor.data.labillion.cn/live/0f47c97f-8098-4f32-a34a-7eb8ea70cb27_1080p.m3u8
- JinLiLite3: https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45feda5_1080p.m3u8
```

### ChiWen 平台
```
- ChiWen1: https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb2_1080p.m3u8
- ChiWen2: https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb3_1080p.m3u8
- ChiWen3: https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb4_1080p.m3u8
```

## 工具返回格式

所有工具返回统一格式：

### 成功响应
```json
{
  "status": "success",
  "action": "operation_name",
  "data": {
    "message": "操作描述",
    // 根据操作类型的额外数据
  }
}
```

### 错误响应
```json
{
  "status": "error",
  "action": "operation_name",
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

## 用户交互示例

### 示例 1: 列出摄像头
**用户**: "JinLiLite平台有哪些摄像头？"

**流程**:
1. 意图识别 → Monitor Agent
2. Monitor Agent 调用 `list_cameras` 工具
3. 返回 JinLiLite 平台的 3 个摄像头列表

### 示例 2: 放大摄像头
**用户**: "把ChiWen1放大到全屏"

**流程**:
1. 意图识别 → Monitor Agent
2. Monitor Agent 调用 `zoom_camera` 工具，参数: camera_name="ChiWen1", zoom_level="fullscreen"
3. 返回摄像头 URL 和操作成功消息

### 示例 3: 隐藏摄像头
**用户**: "隐藏所有JinLiLite的摄像头"

**流程**:
1. 意图识别 → Monitor Agent
2. Monitor Agent 调用 `hide_all_cameras` 工具，参数: platform="JinLiLite"
3. 返回隐藏的摄像头列表

## 测试

### 单元测试
```bash
python test_monitor_agent.py
```
测试内容:
- Monitor State 功能
- Monitor Tools 功能
- Monitor Agent 初始化
- Tools 定义格式

### 集成测试
```bash
python test_monitor_integration.py
```
测试内容:
- Monitor Agent 与 LLM 的集成
- 工具直接执行
- 状态管理
- AgentType 枚举

## 配置

### config.py
新增配置项:
```python
# Monitor Agent 配置
MONITOR_MODEL_NAME = os.getenv("MONITOR_MODEL_NAME", "qwen-plus")
```

可通过环境变量 `MONITOR_MODEL_NAME` 自定义 Monitor Agent 使用的 LLM 模型。

## 文件结构

```
core/agents/
├── __init__.py                 # 导出所有Agent
├── base_agent.py               # Base Agent 基类
├── ai_native_agent.py          # AI-Native Agent
├── organoid_agent.py           # Organoid Agent
├── monitor_agent.py            # Monitor Agent [新增]
├── monitor_state.py            # Monitor 状态管理 [新增]
└── monitor_tools.py            # Monitor 工具定义 [新增]

core/
└── llm.py                      # LLM 包装器（已更新）

config.py                       # 配置文件（已更新）

test_monitor_agent.py           # Monitor Agent 单元测试 [新增]
test_monitor_integration.py     # Monitor Agent 集成测试 [新增]
```

## 工作流程

```
用户输入（文本或语音）
        ↓
ASR 识别（如果是语音）
        ↓
LLM 意图识别
        ↓
选择 Agent
  ├─ Monitor Agent ← 监控相关请求
  ├─ Organoid Agent ← 深度推理请求
  └─ AI-Native Agent ← 普通对话
        ↓
Agent 处理（Monitor Agent 执行工具调用）
        ↓
返回结果给前端
        ↓
TTS 合成（如需要）
        ↓
返回音频给用户
```

## 关键特性

1. **自动意图识别**: 无需指定 Agent，系统自动识别并路由
2. **工具调用循环**: Agent 能够多次调用工具直到完成任务
3. **状态管理**: 实时维护摄像头的可见性和缩放状态
4. **统一返回格式**: 所有工具返回格式一致，便于前端处理
5. **完整的错误处理**: 所有操作都有错误处理和日志记录

## 注意事项

1. **意图识别依赖LLM**: 意图识别需要配置有效的 `LLM_API_KEY` 和 `LLM_BASE_URL`
2. **模型选择**: 可通过 `MONITOR_MODEL_NAME` 环境变量选择专用模型
3. **状态持久化**: 当前状态存储在内存中，重启后会重置。需要持久化存储可自行扩展
4. **并发处理**: 如需支持多用户并发，需要改进状态管理（如添加用户标识）

## 下一步扩展

1. **数据库持久化**: 将摄像头配置和状态存储到数据库
2. **用户隔离**: 为不同用户维护不同的摄像头状态视图
3. **更多操作**: 添加录制、截图等高级功能
4. **实时推送**: 通过 WebSocket 实时推送状态更新
5. **权限控制**: 基于用户角色的访问控制
