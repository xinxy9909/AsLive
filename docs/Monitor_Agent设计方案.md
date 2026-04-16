# Monitor Agent 设计方案

## 一、概述

Monitor Agent 是一个用于管理视频监控的智能Agent，支持用户通过自然语言对视频监控进行各种操作，包括查看、放大、隐藏等功能。

## 二、支持的平台及摄像头

### JinLiLite 平台
- **JinLiLite1**: https://monitor.data.labillion.cn/live/0f47c97f-8098-4f32-a34a-7eb8ea70cb26_1080p.m3u8
- **JinLiLite2**: https://monitor.data.labillion.cn/live/0f47c97f-8098-4f32-a34a-7eb8ea70cb27_1080p.m3u8
- **JinLiLite3**: https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45feda5_1080p.m3u8

### ChiWen 平台
- **ChiWen1**: https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb2_1080p.m3u8
- **ChiWen2**: https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb3_1080p.m3u8
- **ChiWen3**: https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb4_1080p.m3u8

## 三、功能定义

### 1. 查看平台所有摄像头 (List Cameras)
- **功能描述**: 显示某个平台的全部视频监控
- **输入参数**: platform (JinLiLite | ChiWen)
- **输出**: 返回该平台下所有摄像头的列表，包含名称和URL

### 2. 放大摄像头 (Zoom Camera)
- **功能描述**: 将指定摄像头的画面放大到全屏或指定区域
- **输入参数**: camera_name, zoom_level (可选，默认全屏)
- **输出**: 返回操作状态及摄像头URL

### 3. 隐藏摄像头 (Hide Camera)
- **功能描述**: 隐藏指定的摄像头画面
- **输入参数**: camera_name
- **输出**: 返回隐藏操作的状态

### 4. 隐藏所有摄像头 (Hide All Cameras)
- **功能描述**: 隐藏指定平台或所有平台的全部摄像头
- **输入参数**: platform (可选，不指定则隐藏所有)
- **输出**: 返回操作状态及隐藏摄像头的列表

### 5. 显示摄像头 (Show Camera)
- **功能描述**: 显示之前隐藏的摄像头
- **输入参数**: camera_name
- **输出**: 返回显示操作的状态

### 6. 获取摄像头状态 (Get Camera Status)
- **功能描述**: 查询指定摄像头或所有摄像头的当前状态
- **输入参数**: camera_name (可选)
- **输出**: 返回摄像头的可见状态、所属平台等信息

## 四、Tool 定义

### Tool 1: list_cameras
```
{
  "name": "list_cameras",
  "description": "列出指定平台的所有摄像头",
  "parameters": {
    "type": "object",
    "properties": {
      "platform": {
        "type": "string",
        "description": "平台名称: JinLiLite 或 ChiWen",
        "enum": ["JinLiLite", "ChiWen"]
      }
    },
    "required": ["platform"]
  }
}
```

### Tool 2: zoom_camera
```
{
  "name": "zoom_camera",
  "description": "放大指定的摄像头，使其全屏显示或指定大小",
  "parameters": {
    "type": "object",
    "properties": {
      "camera_name": {
        "type": "string",
        "description": "摄像头名称，如 JinLiLite1, ChiWen2 等"
      },
      "zoom_level": {
        "type": "string",
        "description": "放大级别: fullscreen(全屏), large(大), medium(中), small(小)",
        "enum": ["fullscreen", "large", "medium", "small"],
        "default": "fullscreen"
      }
    },
    "required": ["camera_name"]
  }
}
```

### Tool 3: hide_camera
```
{
  "name": "hide_camera",
  "description": "隐藏指定的摄像头",
  "parameters": {
    "type": "object",
    "properties": {
      "camera_name": {
        "type": "string",
        "description": "摄像头名称"
      }
    },
    "required": ["camera_name"]
  }
}
```

### Tool 4: hide_all_cameras
```
{
  "name": "hide_all_cameras",
  "description": "隐藏指定平台或所有平台的全部摄像头",
  "parameters": {
    "type": "object",
    "properties": {
      "platform": {
        "type": "string",
        "description": "平台名称，不指定则隐藏所有平台",
        "enum": ["JinLiLite", "ChiWen"],
        "default": "all"
      }
    }
  }
}
```

### Tool 5: show_camera
```
{
  "name": "show_camera",
  "description": "显示之前隐藏的摄像头",
  "parameters": {
    "type": "object",
    "properties": {
      "camera_name": {
        "type": "string",
        "description": "摄像头名称"
      }
    },
    "required": ["camera_name"]
  }
}
```

### Tool 6: get_camera_status
```
{
  "name": "get_camera_status",
  "description": "获取摄像头或所有摄像头的状态信息",
  "parameters": {
    "type": "object",
    "properties": {
      "camera_name": {
        "type": "string",
        "description": "摄像头名称，不指定则返回所有摄像头状态"
      }
    }
  }
}
```

## 五、返回格式规范

所有Tool返回的格式应遵循以下结构：

### 成功响应
```json
{
  "status": "success",
  "action": "operation_name",
  "data": {
    "cameras": [...],
    "message": "操作成功描述"
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

### 具体示例

#### list_cameras 返回示例
```json
{
  "status": "success",
  "action": "list_cameras",
  "data": {
    "platform": "JinLiLite",
    "cameras": [
      {
        "name": "JinLiLite1",
        "url": "https://monitor.data.labillion.cn/live/0f47c97f-8098-4f32-a34a-7eb8ea70cb26_1080p.m3u8",
        "visible": true,
        "status": "online"
      },
      {
        "name": "JinLiLite2",
        "url": "https://monitor.data.labillion.cn/live/0f47c97f-8098-4f32-a34a-7eb8ea70cb27_1080p.m3u8",
        "visible": true,
        "status": "online"
      },
      {
        "name": "JinLiLite3",
        "url": "https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45feda5_1080p.m3u8",
        "visible": false,
        "status": "online"
      }
    ]
  }
}
```

#### zoom_camera 返回示例
```json
{
  "status": "success",
  "action": "zoom_camera",
  "data": {
    "camera_name": "JinLiLite1",
    "zoom_level": "fullscreen",
    "url": "https://monitor.data.labillion.cn/live/0f47c97f-8098-4f32-a34a-7eb8ea70cb26_1080p.m3u8",
    "message": "已将 JinLiLite1 放大到全屏"
  }
}
```

#### hide_camera 返回示例
```json
{
  "status": "success",
  "action": "hide_camera",
  "data": {
    "camera_name": "JinLiLite1",
    "visible": false,
    "message": "已隐藏 JinLiLite1"
  }
}
```

#### hide_all_cameras 返回示例
```json
{
  "status": "success",
  "action": "hide_all_cameras",
  "data": {
    "platform": "JinLiLite",
    "hidden_cameras": ["JinLiLite1", "JinLiLite2", "JinLiLite3"],
    "message": "已隐藏 JinLiLite 平台的全部摄像头"
  }
}
```

## 六、Agent 工作流程

1. **用户请求输入**: 接收用户的自然语言请求
2. **LLM 解析**: LLM 理解用户意图并选择合适的Tool
3. **Tool 调用**: 执行选定的Tool，获取返回结果
4. **结果处理**: LLM 处理Tool返回的数据
5. **循环检查**: 如果需要额外操作，继续调用Tool；否则生成最终响应
6. **前端交互**: 返回格式化的数据给前端，前端根据action和data执行对应操作

### 工作流程图
```
用户输入
  ↓
LLM 解析意图
  ↓
选择 Tool ← Tool 列表
  ↓
执行 Tool
  ↓
返回结果
  ↓
是否需要继续？
  ├─ 是 → 回到 LLM 解析意图
  └─ 否 → 返回最终响应给前端
```

## 七、用户请求示例

| 用户请求 | 触发的Tool | 说明 |
|---------|----------|------|
| "显示JinLiLite平台的所有摄像头" | list_cameras | platform=JinLiLite |
| "放大JinLiLite1" | zoom_camera | camera_name=JinLiLite1, zoom_level=fullscreen |
| "隐藏ChiWen2" | hide_camera | camera_name=ChiWen2 |
| "隐藏所有摄像头" | hide_all_cameras | platform=all |
| "隐藏JinLiLite平台的所有摄像头" | hide_all_cameras | platform=JinLiLite |
| "显示ChiWen1" | show_camera | camera_name=ChiWen1 |
| "查看所有摄像头的状态" | get_camera_status | 不指定camera_name |
| "JinLiLite1现在的状态如何" | get_camera_status | camera_name=JinLiLite1 |

## 八、实现要点

1. **状态管理**: 需要维护摄像头的可见/隐藏状态
2. **错误处理**: 处理无效的摄像头名称、平台名称等
3. **数据验证**: 验证用户输入的参数是否有效
4. **日志记录**: 记录所有操作以便审计和调试
5. **性能考虑**: 对于大量摄像头的场景需要优化查询效率

## 九、与前端的交互协议

前端应该：
1. 监听来自Agent的返回消息，检查`status`和`action`字段
2. 根据`action`类型执行对应的UI操作
3. 从`data`字段提取需要的摄像头信息和URL
4. 显示`message`字段中的用户友好的操作结果说明

后端Agent应该：
1. 确保所有返回都遵循标准格式
2. 在执行操作前验证参数有效性
3. 返回详细的错误信息便于前端调试
4. 提供足够的元数据供前端使用（如摄像头URL、状态等）
