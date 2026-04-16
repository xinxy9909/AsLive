# Monitor Agent 快速开始指南

## 概述

Monitor Agent 已成功集成到 AsLive 项目。无需额外配置，该 Agent 通过 LLM 意图识别自动激活，处理所有监控相关的用户请求。

## 快速开始

### 1. 验证安装

运行测试脚本确保 Monitor Agent 正常工作：

```bash
# 单元测试
python test_monitor_agent.py

# 集成测试
python test_monitor_integration.py
```

预期输出：两个测试都应该通过所有检查。

### 2. 启动服务

```bash
python api_server.py
```

服务将在 `http://localhost:8000` 上运行。

### 3. 测试 Monitor Agent

#### 使用 curl 测试（文本）

```bash
# 列出摄像头
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "JinLiLite平台有哪些摄像头？"}'

# 放大摄像头
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "把ChiWen1放大到全屏"}'

# 隐藏摄像头
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "隐藏JinLiLite2"}'
```

#### 使用 Python 测试

```python
import requests
import json

# 发送请求
response = requests.post(
    'http://localhost:8000/chat',
    json={'text': '显示所有ChiWen摄像头'}
)

# 解析 SSE 响应
for line in response.iter_lines():
    if line.startswith(b'data: '):
        data = json.loads(line[6:])
        print(data)
```

## 支持的命令示例

### 摄像头查询

| 用户命令 | 效果 |
|---------|------|
| "JinLiLite平台有哪些摄像头？" | 列出 JinLiLite 的 3 个摄像头 |
| "显示所有摄像头" | 显示全部 6 个摄像头 |
| "ChiWen1的状态怎样？" | 查询 ChiWen1 的当前状态 |

### 摄像头控制

| 用户命令 | 效果 |
|---------|------|
| "把ChiWen1放大到全屏" | ChiWen1 缩放级别设为 fullscreen |
| "隐藏JinLiLite1" | 隐藏 JinLiLite1 |
| "显示JinLiLite2" | 显示 JinLiLite2 |
| "隐藏整个JinLiLite平台" | 隐藏 JinLiLite 的所有摄像头 |
| "显示所有摄像头" | 显示全部 6 个摄像头 |

## 架构说明

```
用户请求 → LLM 意图识别 → Monitor Agent → 工具调用 → 返回结果
```

**关键点**:
- **无需新的 API 端点**: 使用现有的 `/chat` 和 `/audio` 接口
- **自动路由**: LLM 自动识别监控相关请求并路由到 Monitor Agent
- **工具调用**: Monitor Agent 调用相应工具完成用户请求
- **统一响应**: 所有操作返回统一的 JSON 格式

## 文件结构

```
core/agents/
├── monitor_agent.py      # Monitor Agent 核心类
├── monitor_state.py      # 摄像头状态管理
├── monitor_tools.py      # 工具定义和实现
└── __init__.py           # 导出 Monitor Agent

core/llm.py              # 更新了意图识别，添加 Monitor Agent 路由
config.py                # 添加 MONITOR_MODEL_NAME 配置

test_monitor_agent.py           # 单元测试
test_monitor_integration.py      # 集成测试

MONITOR_AGENT_INTEGRATION.md     # 完整集成文档
MONITOR_AGENT_SUMMARY.md         # 项目总结
```

## 常见问题

### Q: Monitor Agent 怎样自动调用？
**A**: 当用户提出包含监控相关关键词的请求时，LLM 会自动识别并路由到 Monitor Agent。无需用户或前端特殊处理。

### Q: 如何添加新摄像头？
**A**: 编辑 `core/agents/monitor_state.py` 中的 `CAMERA_CONFIG` 字典，按照现有格式添加新摄像头的配置。

### Q: 摄像头状态是否持久化？
**A**: 当前不持久化。重启服务后状态重置为初始状态（所有摄像头可见，无缩放）。

### Q: 可以通过语音控制吗？
**A**: 可以。使用 `/audio` 端点上传音频，系统会自动 ASR 识别，然后按同样流程处理。

### Q: 如何调试意图识别？
**A**: 查看日志输出，会显示选择的 Agent 类型。如果总是选择 AI-Native Agent，可能是 LLM 识别不准确，可调整系统提示词。

## 需要帮助？

查看详细文档：
- `MONITOR_AGENT_INTEGRATION.md` - 完整的架构和功能说明
- `MONITOR_AGENT_SUMMARY.md` - 项目交付清单和实现总结
- 代码注释 - 所有核心代码都有详细注释

## 后续步骤

### 立即可做
1. ✅ 运行测试确保一切正常
2. ✅ 尝试各种自然语言命令
3. ✅ 查看日志理解工作流程

### 可选增强
1. 前端界面 - 创建监控视图
2. 数据持久化 - 保存摄像头状态到数据库
3. 高级功能 - 添加录制、截图等功能
4. 权限管理 - 基于用户角色的访问控制

---

**Monitor Agent 已准备就绪，可以直接使用！** 🎉
