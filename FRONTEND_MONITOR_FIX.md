# 前端摄像头显示修复

## 问题描述

虽然后端 Monitor Agent 的摄像头默认为关闭状态（`visible=False`），但前端在页面加载时仍然默认显示视频监控面板。这与后端的安全设计不一致。

## 根本原因

前端配置文件 `static/monitor-config.js` 中：
1. 所有监控的 `enabled` 属性设置为 `true`
2. `defaultView` 设置为 `'ui'`，导致页面加载时自动显示监控

## 解决方案

### 1. 修改监控配置（monitor-config.js）

**改动点 1**: 设置摄像头初始状态为关闭
```javascript
// 之前
{
    id: 'monitor-1',
    enabled: true
}

// 现在
{
    id: 'monitor-1',
    enabled: false  // 默认关闭
}
```

对所有 3 个监控都做了相同修改。

**改动点 2**: 改变默认显示模式
```javascript
// 之前
defaultView: 'ui',

// 现在
defaultView: 'none',
```

**改动点 3**: 添加 'none' 模式支持
```javascript
// 添加新代码处理 'none' 模式
if (MONITOR_CONFIG.defaultView === 'none') {
    window.monitorController.hideAllMonitors();
}
```

## 验证修改

修改后的效果：

```
页面加载流程：
1. HTML 加载
2. App.js 初始化
3. Monitor Config 初始化
4. 所有监控设置为 enabled: false
5. defaultView 设置为 'none'
6. 调用 hideAllMonitors() 隐藏所有监控面板
7. 页面显示为空，没有视频流
```

## 用户操作

现在用户需要通过以下方式打开监控：

### 文本命令
```
"显示所有摄像头"
"显示 ChiWen1"
"打开监控"
```

### 控制菜单
点击 "MONITOR CONTROL" 菜单中的 "Show All" 按钮

### 自然语言
```
"打开所有监控"
"显示 JinLiLite 平台的摄像头"
"把 ChiWen1 放大到全屏"
```

## 配置选项

如果需要改变默认行为，可以编辑 `monitor-config.js` 中的 `defaultView`:

```javascript
// 选项：
'none'    // 默认隐藏所有 ✅ (当前设置)
'ui'      // 默认显示为 UI 面板
'3d'      // 默认显示为 3D 场景
'both'    // 同时显示 UI 和 3D
```

## 前后对比

### 修改前
```
页面加载 → 摄像头自动显示 → 视频流开始 ❌
```

### 修改后
```
页面加载 → 摄像头保持关闭 → 用户明确请求时打开 ✅
```

## 安全意义

- ✅ 防止无意中启动视频流
- ✅ 保护用户隐私
- ✅ 节约带宽资源
- ✅ 与后端安全设计一致
- ✅ 符合最佳实践

## 修改文件

```
static/monitor-config.js
  - 更改 enabledFalse 为所有摄像头（行 28, 34, 40）
  - 更改 defaultView 从 'ui' 为 'none'（行 12）
  - 添加 'none' 模式处理逻辑（行 141-143）
```

## Git 提交

```
Commit: 6c5417f
Message: fix: hide all monitors by default on page load
```

## 测试验证

1. **清除浏览器缓存**
   ```
   Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
   ```

2. **重新加载页面**
   ```
   F5 或 Ctrl+R
   ```

3. **验证结果**
   - 页面应该加载完成，不显示任何视频监控面板 ✓
   - 监控区域应该空白 ✓

4. **测试打开监控**
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"text": "显示所有摄像头"}'
   ```
   - 应该看到监控面板出现 ✓

## 注意事项

- 修改只影响前端初始化行为
- 后端监控 Agent 功能不变
- 所有监控工具仍然可用
- 用户可以随时通过 LLM 指令打开/关闭监控

## 问题排查

如果页面加载后仍然显示监控：

1. **清除浏览器缓存**
   ```
   Ctrl+Shift+Delete
   ```

2. **检查浏览器开发者工具**
   ```
   F12 → Network → 检查 monitor-config.js 是否最新
   ```

3. **检查 defaultView 值**
   在浏览器控制台运行：
   ```javascript
   console.log(MONITOR_CONFIG.defaultView)  // 应该输出 'none'
   ```

---

**修复完成！** 前端和后端现在完全一致，摄像头默认关闭。
