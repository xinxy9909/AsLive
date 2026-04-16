// --- 监控系统配置文件 ---

/**
 * 监控视频流配置
 * 修改这里来配置你的监控视频
 */
const MONITOR_CONFIG = {
    // 启用监控系统
    enabled: true,
    
    // 默认显示模式: 'ui' | '3d' | 'both' | 'none'
    // 改为 'none' 以默认隐藏所有监控
    defaultView: 'none',
    
    // 3D默认布局: 'ring' | 'screen' | 'spherical'
    default3DLayout: 'ring',
    
    // 监控面板尺寸
    panelWidth: 320,
    panelHeight: 180,
    
    // 监控列表
    monitors: [
        {
            id: 'monitor-1',
            name: '监控 #1',
            url: 'https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb2_1080p.m3u8',
            description: '主进出口',
            enabled: false  // 默认关闭
        },
        {
            id: 'monitor-2',
            name: '监控 #2',
            url: 'https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb3_1080p.m3u8',
            description: '走廊区域',
            enabled: false  // 默认关闭
        },
        {
            id: 'monitor-3',
            name: '监控 #3',
            url: 'https://monitor.data.labillion.cn/live/8825673d-4ad5-4bae-9345-d5edb45fedb4_1080p.m3u8',
            description: '工作区域',
            enabled: false  // 默认关闭
        }
    ],
    
    // HLS.js配置
    hlsConfig: {
        enableWorker: true,
        lowLatencyMode: true,
        maxBufferLength: 5,
        testOnLoad: false,
        maxLoadingDelay: 4,
        minAutoBitrateLevelCapping: -1,
        autoStartLoad: true
    },
    
    // UI配置
    ui: {
        // 监控面板位置: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
        position: 'bottom-right',
        
        // 展示菜单
        showMenu: true,
        
        // 显示状态指示器
        showStatus: true,
        
        // 启用快捷键
        enableShortcuts: true,
        
        // 自动隐藏不活跃监控（毫秒，0=禁用）
        autoHideTimeout: 0
    },
    
    // 3D场景配置
    scene3D: {
        // 球体半径
        sphereRadius: 12,
        
        // 屏幕间距
        spacing: 8,
        
        // 启用环境光
        enableLighting: true,
        
        // 启用动画效果
        enableAnimation: true,
        
        // 动画速度 (0-1)
        animationSpeed: 0.5
    },
    
    // 调试模式
    debug: false,
    
    // 日志级别: 'none' | 'error' | 'warn' | 'info' | 'debug'
    logLevel: 'info'
};

/**
 * 初始化监控系统配置
 * 在app.js加载后调用
 */
function initializeMonitorConfig() {
    if (!MONITOR_CONFIG.enabled) {
        console.log('Monitor system is disabled');
        return;
    }
    
    console.log('Initializing Monitor Config...', MONITOR_CONFIG);
    
    // 延迟以确保所有系统都已初始化
    setTimeout(() => {
        // 添加所有配置的监控
        MONITOR_CONFIG.monitors.forEach(monitor => {
            if (monitor.enabled) {
                window.monitorManager.addMonitor({
                    id: monitor.id,
                    name: monitor.name,
                    url: monitor.url,
                    width: MONITOR_CONFIG.panelWidth,
                    height: MONITOR_CONFIG.panelHeight
                });
                
                if (MONITOR_CONFIG.debug) {
                    console.log(`Added monitor: ${monitor.id} - ${monitor.name}`);
                }
            }
        });
        
        // 根据配置显示监控
        if (MONITOR_CONFIG.defaultView === 'ui' || MONITOR_CONFIG.defaultView === 'both') {
            window.monitorController.showAllMonitors();
        }
        
        if (MONITOR_CONFIG.defaultView === '3d' || MONITOR_CONFIG.defaultView === 'both') {
            setTimeout(() => {
                window.monitorController.showAllIn3D();
            }, 1000);
        }
        
        // 如果是 'none' 模式，默认隐藏所有监控
        if (MONITOR_CONFIG.defaultView === 'none') {
            window.monitorController.hideAllMonitors();
        }
        
        // 设置默认3D布局
        if (window.monitor3D) {
            window.monitor3D.layoutConfig.spacing = MONITOR_CONFIG.scene3D.spacing;
            window.monitor3D.layoutConfig.sphereRadius = MONITOR_CONFIG.scene3D.sphereRadius;
        }
        
        console.log('Monitor Config initialized successfully');
    }, 1000);
}

/**
 * 动态添加监控
 */
function addMonitorDynamically(id, name, url) {
    window.monitorManager.addMonitor({
        id: id,
        name: name,
        url: url,
        width: MONITOR_CONFIG.panelWidth,
        height: MONITOR_CONFIG.panelHeight
    });
    
    // 立即显示
    window.monitorManager.showMonitor(id);
}

/**
 * 更新HLS配置
 */
function updateHLSConfig(newConfig) {
    MONITOR_CONFIG.hlsConfig = {
        ...MONITOR_CONFIG.hlsConfig,
        ...newConfig
    };
    
    console.log('HLS Config updated:', MONITOR_CONFIG.hlsConfig);
}

/**
 * 启用/禁用调试模式
 */
function setDebugMode(enabled) {
    MONITOR_CONFIG.debug = enabled;
    MONITOR_CONFIG.logLevel = enabled ? 'debug' : 'info';
    
    console.log('Debug mode:', enabled);
}

/**
 * 获取当前配置
 */
function getMonitorConfig() {
    return MONITOR_CONFIG;
}

/**
 * 重置为默认配置
 */
function resetMonitorConfig() {
    // 隐藏所有监控
    window.monitorController.hideAllMonitors();
    
    // 重新初始化
    initializeMonitorConfig();
}

/**
 * 导出配置为JSON（用于备份）
 */
function exportMonitorConfig() {
    const config = JSON.stringify(MONITOR_CONFIG, null, 2);
    
    // 创建下载
    const blob = new Blob([config], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'monitor-config.json';
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * 从JSON导入配置
 */
function importMonitorConfig(jsonString) {
    try {
        const newConfig = JSON.parse(jsonString);
        Object.assign(MONITOR_CONFIG, newConfig);
        console.log('Config imported successfully');
        initializeMonitorConfig();
    } catch (e) {
        console.error('Failed to import config:', e);
    }
}

// 全局API别名
window.monitorConfig = {
    get: getMonitorConfig,
    reset: resetMonitorConfig,
    export: exportMonitorConfig,
    import: importMonitorConfig,
    addMonitor: addMonitorDynamically,
    updateHLS: updateHLSConfig,
    setDebug: setDebugMode
};
