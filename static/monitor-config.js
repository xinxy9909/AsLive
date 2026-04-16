// --- 监控系统配置文件 ---

/**
 * 监控视频流配置
 * 注意：具体的摄像头配置由后端通过 tool_action 事件下发
 * 前端不再硬编码摄像头信息，而是动态接收后端数据
 */
const MONITOR_CONFIG = {
    // 启用监控系统
    enabled: true,
    
    // 默认显示模式: 'ui' | '3d' | 'both' | 'none'
    // 改为 'none' 以默认隐藏所有监控（所有摄像头默认关闭）
    defaultView: 'none',
    
    // 3D默认布局: 'ring' | 'screen' | 'spherical'
    default3DLayout: 'ring',
    
    // 监控面板尺寸
    panelWidth: 320,
    panelHeight: 180,
    
    // 监控列表 - 已弃用
    // 摄像头配置现在由后端通过 tool_action 事件下发
    // 前端动态创建摄像头，无需在此配置
    monitors: [],
    
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
        return;
    }
    
    setTimeout(() => {
        if (MONITOR_CONFIG.defaultView === 'ui' || MONITOR_CONFIG.defaultView === 'both') {
            window.monitorController.showAllMonitors();
        }
        
        if (MONITOR_CONFIG.defaultView === '3d' || MONITOR_CONFIG.defaultView === 'both') {
            setTimeout(() => {
                window.monitorController.showAllIn3D();
            }, 1000);
        }
        
        if (MONITOR_CONFIG.defaultView === 'none') {
            window.monitorController.hideAllMonitors();
        }
        
        if (window.monitor3D) {
            window.monitor3D.layoutConfig.spacing = MONITOR_CONFIG.scene3D.spacing;
            window.monitor3D.layoutConfig.sphereRadius = MONITOR_CONFIG.scene3D.sphereRadius;
        }
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
}

/**
 * 启用/禁用调试模式
 */
function setDebugMode(enabled) {
    MONITOR_CONFIG.debug = enabled;
    MONITOR_CONFIG.logLevel = enabled ? 'debug' : 'info';
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
    window.monitorController.hideAllMonitors();
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
