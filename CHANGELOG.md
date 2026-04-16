# 更新日志

## [2024-04-16] LLM 意图识别和多 Agent 路由改造

### 新增功能

#### 1. Agent 类型系统
- 新增 `AgentType` 枚举，支持 5 种 Agent 类型
  - `ai-native`: Labillion AI-Native（默认）
  - `openai`: OpenAI API
  - `search`: 搜索 Agent
  - `code`: 代码分析 Agent
  - `knowledge`: 知识库 Agent

#### 2. 意图识别器 (IntentClassifier)
- 使用 **LLM 本身** 进行意图识别，而非关键词匹配
- 自动调用 AI-Native API 分析用户意图
- 支持多语言（中英文等）
- 完善的错误处理和回退机制

#### 3. LLMWrapper 增强
- 新增 `enable_intent_classification` 参数，控制是否启用意图识别
- 新增 `select_agent()` 方法，主动选择 Agent
- 新增 `_execute_agent()` 和相关执行方法，支持不同 Agent 的调用
- 所有推理接口（`inference`, `inference_stream`, `inference_stream_chat`）都已升级

#### 4. Agent 执行实现
- **AI-Native**: 直接调用 Labillion API
- **OpenAI**: 调用 OpenAI API（如果配置了 API Key）
- **Search**: AI-Native + 搜索增强提示词
- **Code**: AI-Native + 代码增强提示词
- **Knowledge**: AI-Native + 知识增强提示词

### 改动详情

#### 文件: `core/llm.py`
- 新增导入：`re`, `Enum` 类型支持
- 新增 `AgentType` 枚举类
- 新增配置：`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `DEFAULT_AGENT`
- 新增 `IntentClassifier` 类（约 80 行）
- 扩展 `LLMWrapper` 类（从 20 行扩展到 200+ 行，新增 8 个方法）
- 完整保留原有 AI-Native 调用逻辑

#### 文件: `docs/LLM意图识别和多Agent路由.md`
- 完整的功能说明文档
- 配置指南
- 工作流程图
- 各 Agent 执行方案对比
- 使用示例
- 常见问题解答
- 后续优化方向

#### 文件: `test_intent_classification.py`
- 新增测试脚本，演示意图识别和多 Agent 功能

### 环境变量配置

```bash
# 默认 Agent（默认值: ai-native）
DEFAULT_AGENT=ai-native

# OpenAI 配置（可选）
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# Labillion 配置（必需）
LABILLION_BASE_URL=https://staging.automation.labillion.cn
LABILLION_PLATFORM_ID=xxx
LABILLION_USERNAME=xxx
LABILLION_PASSWORD=xxx
LABILLION_TENANT_ID=xxx
```

### 向后兼容性

✅ **完全向后兼容**
- 现有代码无需修改即可运行
- 默认启用意图识别，可通过参数禁用
- 所有原有 API 接口保持不变
- 默认 Agent 为 `ai-native`，确保行为一致

### 使用示例

#### 基础使用（自动意图识别）
```python
from core.llm import LLMWrapper

llm = LLMWrapper()  # 默认启用意图识别

# 编程问题 → 自动选择 Code Agent
for chunk in llm.inference_stream("如何在 Python 中读取 JSON？"):
    print(chunk, end="")

# 最新信息 → 自动选择 Search Agent
for chunk in llm.inference_stream("今年 AI 有哪些进展？"):
    print(chunk, end="")
```

#### 禁用意图识别
```python
llm = LLMWrapper(enable_intent_classification=False)
# 所有请求使用默认 Agent
```

#### 多轮对话
```python
messages = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "请给我代码示例"},
]

# 自动对最后的用户消息进行意图识别
for chunk in llm.inference_stream_chat(messages):
    print(chunk, end="")
```

### 日志记录

所有重要操作都有日志记录：
- Agent 选择过程
- 意图识别结果
- 错误和异常情况

### 已知限制

1. **意图识别延迟**: 每个请求都需要先调用 LLM 识别意图，会增加额外延迟
   - 建议后续添加缓存机制

2. **Search/Code/Knowledge Agent 当前实现**: 
   - 目前通过提示词增强实现，未实际集成搜索引擎或知识库
   - 建议后续集成真实的搜索 API 和知识库

3. **OpenAI Agent**: 
   - 需要配置 OpenAI API Key
   - 如未配置，自动回退到 AI-Native

### 测试

运行测试脚本查看功能演示：
```bash
python test_intent_classification.py
```

### 后续优化方向

1. 意图识别缓存（避免重复识别）
2. 多模型支持（Claude、Gemini 等）
3. 真实搜索引擎集成
4. 知识库系统集成
5. 轻量级意图分类模型（降低延迟）
6. 用户反馈循环（持续优化）

---

**改造者**: AI Assistant  
**改造日期**: 2024-04-16  
**状态**: ✅ 完成
