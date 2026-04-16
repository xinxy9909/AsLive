# Monitor Agent - 视频监控智能控制系统

## 🎯 概述

Monitor Agent 是 AsLive 项目中的第三个智能 Agent，专门用于管理和控制视频监控系统。通过自然语言理解，用户可以轻松控制 6 个分布在 2 个平台上的摄像头。

## ✨ 核心特性

- 🤖 **自动意图识别**: LLM 自动识别监控相关请求
- 🔧 **7 个强大工具**: 列表、缩放、隐藏、显示、状态查询
- 🔒 **安全设计**: 摄像头默认关闭，防止隐私泄露
- 📡 **无需新增接口**: 通过现有的 `/chat` 和 `/audio` 接口使用
- 🎨 **统一返回格式**: 前端易于处理的标准 JSON 响应
- 🧪 **完整测试**: 14+ 单元测试，8+ 集成测试

## 🚀 快速开始

### 1. 启动服务

```bash
python api_server.py
```

### 2. 调用 API

```bash
# 列出摄像头
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "JinLiLite 平台有哪些摄像头？"}'

# 打开摄像头
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "显示 ChiWen1"}'

# 放大摄像头
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "把 JinLiLite1 放大到全屏"}'
```

## 📋 支持的操作

### 摄像头查询
```
"JinLiLite 平台有哪些摄像头？"
"显示所有摄像头"
"ChiWen1 现在的状态是什么？"
```

### 摄像头控制
```
"显示 JinLiLite1"          # 打开单个摄像头
"显示所有 ChiWen 摄像头"   # 打开整个平台
"隐藏 JinLiLite2"          # 关闭单个摄像头
"隐藏所有摄像头"           # 关闭所有摄像头
"把 ChiWen1 放大到全屏"    # 放大摄像头
```

## 📊 支持的摄像头

### JinLiLite 平台 (3 个)
- JinLiLite1
- JinLiLite2
- JinLiLite3

### ChiWen 平台 (3 个)
- ChiWen1
- ChiWen2
- ChiWen3

**初始状态**: 所有摄像头关闭（出于安全考虑）

## 🛠️ 7 个工具

| 工具名 | 功能 | 示例 |
|--------|------|------|
| `list_cameras` | 列出平台的摄像头 | "列出 JinLiLite 的摄像头" |
| `zoom_camera` | 放大摄像头 | "把 ChiWen1 放大" |
| `hide_camera` | 隐藏单个摄像头 | "隐藏 JinLiLite1" |
| `hide_all_cameras` | 隐藏整个平台 | "隐藏所有 ChiWen 摄像头" |
| `show_camera` | 显示摄像头 | "显示 JinLiLite2" |
| `show_all_cameras` | 显示整个平台 | "显示所有摄像头" |
| `get_camera_status` | 查询摄像头状态 | "ChiWen1 的状态?" |

## 📁 文件结构

```
core/agents/
├── monitor_agent.py          # 核心 Agent 类
├── monitor_state.py          # 状态管理
├── monitor_tools.py          # 工具定义
└── __init__.py               # 导出

core/llm.py                   # LLM 意图识别（已更新）
config.py                     # 配置管理（已更新）

test_monitor_agent.py         # 单元测试
test_monitor_integration.py   # 集成测试

MONITOR_AGENT_INTEGRATION.md  # 完整文档
MONITOR_QUICK_START.md        # 快速开始
DELIVERY_CHECKLIST.md         # 交付清单
```

## 🧪 测试

### 运行测试

```bash
# 单元测试
python test_monitor_agent.py

# 集成测试
python test_monitor_integration.py
```

### 测试结果

```
✅ 14+ 单元测试 - 全部通过
✅ 8+ 集成测试 - 全部通过
✅ 初始化: 6 个摄像头，全部关闭
✅ 工具执行: 所有工具正常工作
```

## 📖 文档

详细信息请查看以下文档：

- **[MONITOR_QUICK_START.md](MONITOR_QUICK_START.md)** - 快速开始指南
- **[MONITOR_AGENT_INTEGRATION.md](MONITOR_AGENT_INTEGRATION.md)** - 完整集成文档
- **[MONITOR_AGENT_SUMMARY.md](MONITOR_AGENT_SUMMARY.md)** - 项目总结
- **[CAMERA_VISIBILITY_CHANGE.md](CAMERA_VISIBILITY_CHANGE.md)** - 可见性配置说明
- **[DELIVERY_CHECKLIST.md](DELIVERY_CHECKLIST.md)** - 交付清单

## 🏗️ 架构

```
用户输入 
   ↓
LLM 意图识别
   ↓
自动路由到 Monitor Agent
   ↓
执行工具调用
   ↓
返回结果给用户
```

**关键点**：
- 无需前端修改
- 完全自动化的路由
- 支持工具调用循环
- 统一的 JSON 响应格式

## 🔐 安全性

### 默认关闭设计
- 所有摄像头初始状态为关闭
- 防止无意的视频流启动
- 用户必须显式打开才能使用
- 保护隐私和数据安全

## 🎯 核心 API 端点

Monitor Agent 通过现有接口使用，**无需新增端点**：

| 端点 | 方法 | 用途 |
|------|------|------|
| `/chat` | POST | 文本请求 |
| `/audio` | POST | 语音请求 |
| `/history` | GET | 对话历史 |

## 🔧 配置

### 环境变量

```bash
# 监控 Agent 使用的模型（可选）
MONITOR_MODEL_NAME=qwen-plus

# LLM 配置（必需）
LLM_API_KEY=your_api_key
LLM_BASE_URL=your_llm_url
LLM_MODEL_NAME=your_model_name
```

### 添加新摄像头

编辑 `core/agents/monitor_state.py` 中的 `CAMERA_CONFIG`:

```python
"YourPlatform": [
    {
        "name": "YourCamera1",
        "url": "your_stream_url"
    },
    ...
]
```

## 🚀 部署

### 前置条件
- Python 3.x
- 配置有效的 LLM API

### 启动命令
```bash
python api_server.py
```

### 验证
```bash
python test_monitor_agent.py  # 运行验证测试
```

## 📊 统计

- **代码**: ~1290 行
- **测试**: 22+ 测试用例
- **文档**: 6 份详细文档
- **工具**: 7 个功能完整的工具
- **摄像头**: 6 个（2 个平台）

## ❓ FAQ

**Q: 摄像头状态会被保存吗？**
A: 当前不会。状态存储在内存中，重启后重置。可通过添加数据库支持来实现持久化。

**Q: 如何扩展到支持更多摄像头？**
A: 在 `CAMERA_CONFIG` 中添加新的摄像头配置即可，代码无需修改。

**Q: Monitor Agent 如何自动调用的？**
A: LLM 会识别请求中的监控相关关键词，自动路由到 Monitor Agent。

**Q: 为什么默认关闭摄像头？**
A: 这是安全和隐私的最佳实践，防止无意中启动视频流。

**Q: 可以通过语音控制吗？**
A: 完全可以！使用 `/audio` 接口上传音频，系统会自动处理。

## 📞 支持

遇到问题？

1. 查看 [MONITOR_QUICK_START.md](MONITOR_QUICK_START.md)
2. 运行 `python test_monitor_agent.py` 验证安装
3. 检查日志输出了解执行流程
4. 查阅代码注释了解实现细节

## 📝 版本信息

- **版本**: 1.0
- **发布日期**: 2026-04-16
- **状态**: ✅ 完成并验证

## 📄 许可证

与 AsLive 项目相同的许可证

---

**Monitor Agent 已准备就绪！** 🎉

现在就开始使用吧 → [快速开始指南](MONITOR_QUICK_START.md)
