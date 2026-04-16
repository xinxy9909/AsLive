// --- 监控系统快速开始示例 ---

/**
 * 注意：这个文件中的代码应该在你的应用初始化后运行
 * 建议在 app.js 中的 initializeMonitorSystem() 之后执行
 */

// ================== 快速配置示例 ==================

/**
 * 示例1: 基础配置 - 显示单个监控
 */
function example1_SingleMonitor() {
    // 1. 添加监控配置
    addMonitorConfig(
        'monitor-1',
        '主入口监控',
        'https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb2_1080p.m3u8'
    );
    
    // 2. 显示监控
    showMonitor('monitor-1');
    
    console.log('Single monitor example completed');
}

/**
 * 示例2: 多监控配置 - 显示多个监控
 */
function example2_MultipleMonitors() {
    const monitors = [
        {
            id: 'monitor-1',
            name: '监控室 #1',
            url: 'https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb2_1080p.m3u8'
        },
        {
            id: 'monitor-2',
            name: '监控室 #2',
            url: 'https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb3_1080p.m3u8'
        },
        {
            id: 'monitor-3',
            name: '监控室 #3',
            url: 'https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb4_1080p.m3u8'
        }
    ];
    
    // 添加所有监控
    monitors.forEach(monitor => {
        window.monitorManager.addMonitor({
            id: monitor.id,
            name: monitor.name,
            url: monitor.url,
            width: 320,
            height: 180
        });
    });
    
    // 显示所有监控
    monitorController.showAllMonitors();
    
    console.log('Multiple monitors configured');
}

/**
 * 示例3: 3D集成 - 在3D场景中显示监控
 */
function example3_3DIntegration() {
    // 1. 先显示UI中的监控
    monitorController.showAllMonitors();
    
    // 2. 在3D场景中显示（Ring布局）
    setTimeout(() => {
        monitorController.showAllIn3D();
    }, 1000);
    
    console.log('3D integration example started');
}

/**
 * 示例4: 布局切换 - 动态切换3D布局
 */
function example4_LayoutSwitching() {
    // 显示所有监控
    monitorController.showAllMonitors();
    
    // 初始化为Ring布局
    setTimeout(() => {
        monitorController.showAllIn3D();
    }, 500);
    
    // 2秒后切换到Screen布局
    setTimeout(() => {
        monitorController.switchLayout('screen');
        console.log('Switched to Screen layout');
    }, 2500);
    
    // 4秒后切换到Spherical布局
    setTimeout(() => {
        monitorController.switchLayout('spherical');
        console.log('Switched to Spherical layout');
    }, 4500);
    
    // 6秒后回到Ring布局
    setTimeout(() => {
        monitorController.switchLayout('ring');
        console.log('Switched back to Ring layout');
    }, 6500);
}

/**
 * 示例5: 交互控制 - 动态显示/隐藏
 */
function example5_InteractiveControl() {
    // 配置监控
    monitorController.showAllMonitors();
    
    // 交替显示/隐藏
    let visible = [true, true, true];
    
    setInterval(() => {
        const monitors = ['monitor-1', 'monitor-2', 'monitor-3'];
        
        monitors.forEach((id, index) => {
            visible[index] = !visible[index];
            
            if (visible[index]) {
                showMonitor(id);
            } else {
                hideMonitor(id);
            }
        });
        
        console.log('Toggled monitor visibility');
    }, 3000);
}

/**
 * 示例6: 自定义控制面板
 */
function example6_CustomControlPanel() {
    // 创建自定义控制面板
    const panel = document.createElement('div');
    panel.style.cssText = `
        position: absolute;
        top: 100px;
        right: 30px;
        background: rgba(0, 0, 0, 0.9);
        border: 1px solid #00f2ff;
        border-radius: 12px;
        padding: 20px;
        z-index: 100;
        min-width: 200px;
    `;
    
    panel.innerHTML = `
        <h3 style="color: #00f2ff; margin-bottom: 15px;">监控控制</h3>
        <button id="btn-show-all" style="
            width: 100%;
            padding: 8px;
            margin-bottom: 8px;
            background: #00f2ff;
            color: #000;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        ">显示所有</button>
        <button id="btn-hide-all" style="
            width: 100%;
            padding: 8px;
            margin-bottom: 8px;
            background: #bd00ff;
            color: #fff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        ">隐藏所有</button>
        <button id="btn-toggle-3d" style="
            width: 100%;
            padding: 8px;
            background: #00ff88;
            color: #000;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        ">切换3D显示</button>
    `;
    
    document.getElementById('ui-layer').appendChild(panel);
    
    // 绑定事件
    document.getElementById('btn-show-all').addEventListener('click', () => {
        monitorController.showAllMonitors();
    });
    
    document.getElementById('btn-hide-all').addEventListener('click', () => {
        monitorController.hideAllMonitors();
    });
    
    let show3D = false;
    document.getElementById('btn-toggle-3d').addEventListener('click', () => {
        show3D = !show3D;
        if (show3D) {
            monitorController.showAllIn3D();
        } else {
            monitorController.hideAllFrom3D();
        }
    });
    
    console.log('Custom control panel created');
}

/**
 * 示例7: 监控事件监听
 */
function example7_EventListening() {
    // 添加监控
    addMonitorConfig(
        'monitor-1',
        '测试监控',
        'https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb2_1080p.m3u8'
    );
    
    // 显示监控
    showMonitor('monitor-1');
    
    // 获取视频元素并监听事件
    setTimeout(() => {
        const video = window.monitorManager.videoElements.get('monitor-1');
        
        if (video) {
            video.addEventListener('play', () => {
                console.log('[Event] Monitor 1 started playing');
            });
            
            video.addEventListener('pause', () => {
                console.log('[Event] Monitor 1 paused');
            });
            
            video.addEventListener('loadstart', () => {
                console.log('[Event] Monitor 1 loading started');
            });
            
            video.addEventListener('loadeddata', () => {
                console.log('[Event] Monitor 1 data loaded');
            });
            
            video.addEventListener('error', (e) => {
                console.error('[Event] Monitor 1 error:', e);
            });
        }
    }, 500);
}

/**
 * 示例8: 性能监测
 */
function example8_PerformanceMonitoring() {
    // 定期输出性能指标
    setInterval(() => {
        const activeCount = window.monitorManager.getActiveMonitors().size;
        const display3DCount = window.monitor3D.getAll3DDisplays().size;
        
        console.log('=== Monitor System Performance ===');
        console.log(`Active UI Monitors: ${activeCount}`);
        console.log(`3D Displays: ${display3DCount}`);
        console.log(`Video Elements: ${window.monitorManager.videoElements.size}`);
        console.log(`HLS Players: ${window.monitorManager.players.size}`);
    }, 5000);
}

/**
 * 示例9: 声音激活控制
 */
function example9_AudioActivatedControl() {
    // 当接收到音频输入时显示监控
    
    // 监听micAnalyser的音频数据
    const originalAnimate = window.animate;
    
    let audioLevel = 0;
    let monitorVisible = false;
    
    // 这是一个概念示例，实际整合应在animate()函数中
    document.addEventListener('audioLevelChange', (e) => {
        audioLevel = e.detail.level;
        
        if (audioLevel > 0.5 && !monitorVisible) {
            // 高音量时显示监控
            monitorController.showAllMonitors();
            monitorVisible = true;
        } else if (audioLevel < 0.2 && monitorVisible) {
            // 低音量时隐藏监控
            monitorController.hideAllMonitors();
            monitorVisible = false;
        }
    });
}

/**
 * 示例10: 完整集成示例
 */
function example10_CompleteIntegration() {
    console.log('Starting complete monitor system integration...');
    
    // 步骤1: 配置监控
    console.log('Step 1: Configuring monitors...');
    example2_MultipleMonitors();
    
    // 步骤2: 初始化UI显示
    console.log('Step 2: Initializing UI display...');
    setTimeout(() => {
        monitorController.showAllMonitors();
    }, 500);
    
    // 步骤3: 在3D场景中显示
    console.log('Step 3: Adding to 3D scene...');
    setTimeout(() => {
        monitorController.showAllIn3D();
    }, 1500);
    
    // 步骤4: 启用事件监听
    console.log('Step 4: Setting up event listeners...');
    setTimeout(() => {
        example7_EventListening();
    }, 2000);
    
    // 步骤5: 启用性能监测
    console.log('Step 5: Starting performance monitoring...');
    example8_PerformanceMonitoring();
    
    console.log('Monitor system integration complete!');
}

// ================== 快速执行 ==================

// 取消注释以下任意一个来运行示例
// example1_SingleMonitor();
// example2_MultipleMonitors();
// example3_3DIntegration();
// example4_LayoutSwitching();
// example5_InteractiveControl();
// example6_CustomControlPanel();
// example7_EventListening();
// example8_PerformanceMonitoring();
// example10_CompleteIntegration();

// 或者直接在控制台执行：
// window.runMonitorExample = function(exampleNum) {
//     window[`example${exampleNum}_`]?.();
// };
// runMonitorExample(1);
