# 监控视频集成系统 - 使用指南

## 功能概述

本系统将监控视频有机地集成到现有的3D前端实现中，支持：

- ✅ **HLS流播放** - 使用HLS.js支持M3U8视频流（包括跨域支持）
- ✅ **多监控管理** - 支持同时显示多个监控视频
- ✅ **灵活的显示/隐藏** - 快速切换监控可见性
- ✅ **3D场景集成** - 将监控视频作为3D纹理投影到场景中
- ✅ **多种布局模式** - Ring、Screen、Spherical三种3D布局方式
- ✅ **交互控制** - 播放/暂停、隐藏/显示、布局切换
- ✅ **实时状态反馈** - 显示在线、加载、错误等状态

## 系统架构

### 核心模块

#### 1. **monitor.js** - 监控管理器
```javascript
class MonitorManager
```

主要职责：
- 管理监控配置和生命周期
- 创建/销毁监控UI面板
- 初始化HLS播放器
- 状态管理和事件处理

**主要方法：**
```javascript
// 添加监控配置
monitorManager.addMonitor({
    id: 'monitor-1',
    name: '监控室 #1',
    url: 'https://monitor.data.labillion.cn/live/...m3u8',
    width: 320,
    height: 180
});

// 显示监控
monitorManager.showMonitor('monitor-1');

// 隐藏监控
monitorManager.hideMonitor('monitor-1');

// 播放/暂停切换
monitorManager.togglePlay('monitor-1');
```

#### 2. **monitor-3d.js** - 3D集成模块
```javascript
class Monitor3DIntegration
```

主要职责：
- 创建视频纹理
- 管理3D显示对象
- 支持多种显示布局
- 动画效果和场景增强

**显示模式：**
- `'ring'` - 环形排列，监控围绕球体旋转
- `'screen'` - 浮动屏幕，垂直堆叠显示
- `'spherical'` - 球面投影，贴在球体表面

#### 3. **monitor-control.js** - 控制器
```javascript
class MonitorController
```

主要职责：
- 整合UI和3D系统
- 管理控制菜单和交互
- 提供便捷API和快捷键

## 使用方法

### 基础使用

#### 1. 配置监控视频

在页面加载完成后，添加监控配置：

```javascript
// 方法一：直接API
addMonitorConfig(
    'monitor-1',
    '监控 #1',
    'https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb2_1080p.m3u8'
);

// 方法二：使用Manager
window.monitorManager.addMonitor({
    id: 'monitor-2',
    name: '监控 #2',
    url: 'https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb3_1080p.m3u8',
    width: 320,
    height: 180
});
```

#### 2. 显示/隐藏监控

```javascript
// 显示指定监控
showMonitor('monitor-1');

// 隐藏指定监控
hideMonitor('monitor-1');

// 切换显示/隐藏
toggleMonitor('monitor-1');

// 显示所有监控
monitorController.showAllMonitors();

// 隐藏所有监控
monitorController.hideAllMonitors();
```

#### 3. 3D集成

```javascript
// 将监控添加到3D场景（Ring模式）
monitor3D.showMonitorIn3D('monitor-1', videoElement, 'ring', 0);

// 显示所有监控在3D场景
showAllMonitorsIn3D();

// 切换3D布局模式
switchMonitorLayout('screen');  // 'ring' | 'screen' | 'spherical'
```

### 快捷键

| 快捷键 | 功能 |
|------|------|
| `Alt + M` | 打开/关闭监控菜单 |
| `Alt + 1` | 切换监控1显示/隐藏 |
| `Alt + 2` | 切换监控2显示/隐藏 |
| `Alt + 3` | 切换监控3显示/隐藏 |
| ... | ... |

### 菜单操作

点击控制菜单项目：
- **Show All Monitors** - 显示所有配置的监控
- **Hide All Monitors** - 隐藏所有监控
- **Ring Layout (3D)** - 环形3D布局
- **Screen Layout (3D)** - 屏幕3D布局
- **Sphere Layout (3D)** - 球面3D布局
- **Show in 3D Scene** - 将监控添加到3D场景
- **Hide 3D Scene** - 隐藏3D场景中的监控

## UI组件详解

### 监控面板 (Monitor Panel)

位置：右下角（上方预留给底部控制栏）

**组件结构：**
```
┌─────────────────────┐
│ 监控 #1    [▶] [✕]  │  ← 控制栏
├─────────────────────┤
│                     │
│   视频内容          │
│                     │
└─────────────────────┘
      ONLINE  ← 状态指示
```

**控制按钮：**
- ▶ - 播放/暂停
- ✕ - 隐藏监控

**状态指示器：**
- 🟢 **ONLINE** - 在线，正常播放
- 🔵 **LOADING** - 正在加载
- 🟠 **STALLED** - 缓冲中
- 🔴 **ERROR** - 播放错误
- ⚫ **OFFLINE** - 离线

### 样式特点

- **玻璃态毛玻璃背景** - 半透明模糊效果
- **氰蓝色主题** - 与现有UI配色一致
- **发光边框** - Hover时增强视觉反馈
- **流畅动画** - 显示/隐藏平滑过渡

## 3D布局说明

### Ring Layout (环形)
```
         Monitor 1
        /    |    \
       /     |     \
      /      ●      \  ← 中心球体
     /       |       \
   M3  ------+------ M2
```
- 监控围绕球体环形排列
- 自动面向球心
- 适合多监控同时观看

### Screen Layout (屏幕)
```
  Monitor 1
    Monitor 2
      Monitor 3
         ●
       (球体)
```
- 监控垂直堆叠排列
- 类似浮动屏幕
- 适合依次查看

### Spherical Layout (球面)
```
         Monitor 1
        /    ●    \
       /   (球体)  \
      /    /|\     \
   M2 ----/ | \---- M3
```
- 监控分布在球体周围
- 动态贴附效果
- 适合环境映射

## API参考

### 全局对象

#### monitorManager
```javascript
// 属性
monitorManager.monitors          // Map<id, config>
monitorManager.videoElements     // Map<id, HTMLVideoElement>
monitorManager.activeMonitors    // Set<id>

// 方法
addMonitor(config)
showMonitor(monitorId)
hideMonitor(monitorId)
togglePlay(monitorId)
setStatus(monitorId, status)
getActiveMonitors()
hideAllMonitors()
showAllMonitors()
```

#### monitor3D
```javascript
// 方法
createVideoTexture(monitorId, videoElement)
showMonitorIn3D(monitorId, videoElement, displayMode, index)
removeMonitorFrom3D(monitorId)
switchDisplayMode(monitorId, newMode, videoElement, index)
arrangeMonitorsLayout(monitorElements, layoutMode)
hideAll3D()
showAll3D()
```

#### monitorController
```javascript
// 方法
showAllMonitors()
hideAllMonitors()
switchLayout(layoutMode)
showAllIn3D()
hideAllFrom3D()
toggleMenu()
hideMenu()
```

### 便捷函数

```javascript
// 单个监控操作
showMonitor(monitorId)
hideMonitor(monitorId)
toggleMonitor(monitorId)

// 配置监控
addMonitorConfig(id, name, url)

// 3D操作
switchMonitorLayout(layoutMode)
showAllMonitorsIn3D()
```

## 实现细节

### HLS支持

系统使用**HLS.js**库处理M3U8流：

```javascript
// 自动加载HLS.js CDN
if (!window.HLS) {
    // 从CDN加载: https://cdn.jsdelivr.net/npm/hls.js@1.4.12/dist/hls.min.js
}

// HLS配置优化
{
    enableWorker: true,        // 使用Web Worker
    lowLatencyMode: true,      // 低延迟模式
    maxBufferLength: 5,        // 最大缓冲时间
    testOnLoad: false          // 不测试加载
}
```

### 视频纹理处理

```javascript
// 创建实时视频纹理
const texture = new THREE.VideoTexture(videoElement);
texture.colorSpace = THREE.SRGBColorSpace;
texture.minFilter = THREE.LinearFilter;
texture.magFilter = THREE.LinearFilter;
```

### 状态管理

监控状态转换：
```
OFFLINE
   ↓
LOADING → ONLINE
   ↓       ↓
  ERROR   STALLED
```

## 调试

### 控制台API

```javascript
// 查看所有监控配置
console.log(window.monitorManager.getAllMonitors());

// 查看活跃监控
console.log(window.monitorManager.getActiveMonitors());

// 查看3D显示
console.log(window.monitor3D.getAll3DDisplays());

// 检查视频元素
console.log(window.monitorManager.videoElements);
```

### 常见问题

**1. 视频不显示**
- 检查URL是否正确
- 验证CORS跨域配置
- 查看浏览器控制台错误信息

**2. HLS加载失败**
- 确保HLS.js已加载
- 检查网络连接
- 查看HLS.Events.ERROR事件

**3. 3D显示不出现**
- 确保scene已初始化
- 检查视频元素是否有效
- 验证camera视角

**4. 性能问题**
- 减少同时显示的监控数量
- 关闭3D动画效果
- 使用较低分辨率的视频流

## 自定义扩展

### 添加新的显示模式

```javascript
// 在Monitor3DIntegration中添加新方法
createCustomDisplay(monitorId, videoElement, index) {
    const texture = this.createVideoTexture(monitorId, videoElement);
    const material = new THREE.MeshBasicMaterial({ map: texture });
    
    // 自定义几何体和位置
    const geometry = new THREE.CustomGeometry();
    const mesh = new THREE.Mesh(geometry, material);
    
    // 自定义位置和旋转
    mesh.position.set(/* ... */);
    mesh.rotation.set(/* ... */);
    
    this.scene.add(mesh);
    this.displays3D.set(monitorId, { type: 'custom', mesh, material });
    
    return mesh;
}
```

### 自定义样式

在style.css中修改CSS变量：

```css
:root {
    --monitor-width: 320px;
    --monitor-height: 180px;
    --monitor-bg: rgba(0, 0, 0, 0.8);
    /* ... */
}
```

### 事件监听

```javascript
// 监听视频事件
const video = monitorManager.videoElements.get(monitorId);

video.addEventListener('play', () => {
    console.log('Video started playing');
});

video.addEventListener('error', (e) => {
    console.error('Video error:', e);
});
```

## 性能优化建议

1. **限制并发连接数** - 同时最多3个活跃监控
2. **使用低延迟HLS** - 配置lowLatencyMode为true
3. **缓冲优化** - 调整maxBufferLength参数
4. **内存管理** - 及时调用hideMonitor清理资源
5. **GPU优化** - 使用requestAnimationFrame管理3D渲染

## 许可和引用

- **HLS.js** - https://github.com/video-dev/hls.js
- **Three.js** - https://threejs.org
- **Font Awesome** - https://fontawesome.com
