// --- 监控控制和交互集成模块 ---

/**
 * 监控系统控制器 - 整合监控UI、3D显示和交互
 */
class MonitorController {
    constructor(monitorManager, monitor3D) {
        this.monitorManager = monitorManager;
        this.monitor3D = monitor3D;
        this.isGridMode = false; // Grid vs List view
        this.currentLayout = 'ring'; // 当前3D布局模式
        this.monitorCount = 0;
        
        // 初始化控制菜单
        this.initControlMenu();
    }
    
    /**
     * 初始化控制菜单
     */
    initControlMenu() {
        // 创建菜单容器
        const menu = document.createElement('div');
        menu.id = 'monitor-control-menu';
        menu.className = 'monitor-menu';
        menu.style.display = 'none';
        
        // 菜单头部
        const header = document.createElement('div');
        header.className = 'monitor-menu-header';
        header.innerHTML = '<span class="monitor-menu-title">MONITOR CONTROL</span>';
        menu.appendChild(header);
        
        // 菜单项目
        const menuItems = [
            { id: 'menu-show-all', icon: 'fa-video', text: 'Show All' },
            { id: 'menu-hide-all', icon: 'fa-eye-slash', text: 'Hide All' },
            { id: 'menu-divider1', divider: true },
            { id: 'menu-layout-ring', icon: 'fa-circle-notch', text: 'Ring Layout' },
            { id: 'menu-layout-screen', icon: 'fa-desktop', text: 'Screen Layout' },
            { id: 'menu-layout-sphere', icon: 'fa-globe-americas', text: 'Sphere Layout' },
            { id: 'menu-divider2', divider: true },
            { id: 'menu-show-3d', icon: 'fa-cube', text: 'Show in 3D' },
            { id: 'menu-hide-3d', icon: 'fa-cube', text: 'Hide from 3D' }
        ];
        
        menuItems.forEach(item => {
            if (item.divider) {
                const divider = document.createElement('div');
                divider.className = 'monitor-menu-divider';
                menu.appendChild(divider);
            } else {
                const menuItem = document.createElement('div');
                menuItem.className = 'monitor-menu-item';
                menuItem.id = item.id;
                menuItem.innerHTML = `<i class="fas ${item.icon}"></i><span>${item.text}</span>`;
                menu.appendChild(menuItem);
            }
        });
        
        document.getElementById('ui-layer').appendChild(menu);
        
        // 绑定事件
        document.getElementById('menu-show-all').addEventListener('click', () => {
            this.showAllMonitors();
        });
        
        document.getElementById('menu-hide-all').addEventListener('click', () => {
            this.hideAllMonitors();
        });
        
        document.getElementById('menu-layout-ring').addEventListener('click', () => {
            this.switchLayout('ring');
        });
        
        document.getElementById('menu-layout-screen').addEventListener('click', () => {
            this.switchLayout('screen');
        });
        
        document.getElementById('menu-layout-sphere').addEventListener('click', () => {
            this.switchLayout('spherical');
        });
        
        document.getElementById('menu-show-3d').addEventListener('click', () => {
            this.showAllIn3D();
        });
        
        document.getElementById('menu-hide-3d').addEventListener('click', () => {
            this.hideAllFrom3D();
        });
    }
    
    /**
     * 显示所有监控
     */
    showAllMonitors() {
        this.monitorManager.showAllMonitors();
        this.addMessage('All monitors displayed');
    }
    
    /**
     * 隐藏所有监控
     */
    hideAllMonitors() {
        this.monitorManager.hideAllMonitors();
        this.addMessage('All monitors hidden');
    }
    
    /**
     * 切换3D布局
     * @param {string} layoutMode - 'ring', 'screen', 'spherical'
     */
    switchLayout(layoutMode) {
        this.currentLayout = layoutMode;
        
        const monitors = this.monitorManager.getActiveMonitors();
        const videoElements = this.monitorManager.videoElements;
        
        monitors.forEach((monitorId, index) => {
            const videoElement = videoElements.get(monitorId);
            if (videoElement && this.monitor3D) {
                this.monitor3D.switchDisplayMode(
                    monitorId,
                    layoutMode,
                    videoElement,
                    index
                );
            }
        });
        
        this.addMessage(`Switched to ${layoutMode} layout`);
    }
    
    /**
     * 显示所有监控在3D场景中
     */
    showAllIn3D() {
        const monitors = this.monitorManager.getActiveMonitors();
        const videoElements = this.monitorManager.videoElements;
        
        let index = 0;
        monitors.forEach((monitorId) => {
            const videoElement = videoElements.get(monitorId);
            if (videoElement && this.monitor3D) {
                this.monitor3D.showMonitorIn3D(
                    monitorId,
                    videoElement,
                    this.currentLayout,
                    index++
                );
            }
        });
        
        this.addMessage('Monitors added to 3D scene');
    }
    
    /**
     * 隐藏所有3D显示
     */
    hideAllFrom3D() {
        if (this.monitor3D) {
            this.monitor3D.hideAll3D();
        }
        
        this.addMessage('3D monitors hidden');
    }
    
    /**
     * 添加系统消息到聊天历史
     * @param {string} message 
     */
    addMessage(message) {
        const chatHistory = document.getElementById('chat-history');
        if (!chatHistory) return;
        
        const messageEl = document.createElement('div');
        messageEl.className = 'message system';
        messageEl.innerHTML = `<div class="message-content">[MONITOR] ${message}</div>`;
        chatHistory.appendChild(messageEl);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    /**
     * 切换控制菜单显示
     */
    toggleMenu() {
        const menu = document.getElementById('monitor-control-menu');
        if (menu) {
            menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
        }
    }
    
    /**
     * 隐藏控制菜单
     */
    hideMenu() {
        const menu = document.getElementById('monitor-control-menu');
        if (menu) {
            menu.style.display = 'none';
        }
    }
}

/**
 * 全局初始化监控系统
 */
window.initializeMonitorSystem = function(scene) {
    // 初始化监控管理器
    window.monitorManager.initContainer();
    
    // 初始化3D集成
    window.monitor3D = new Monitor3DIntegration(scene);
    window.monitor3D.enhanceSceneLighting();
    
    // 创建控制器
    window.monitorController = new MonitorController(
        window.monitorManager,
        window.monitor3D
    );
    
    // 添加快捷键支持
    setupMonitorShortcuts();
    
    console.log('Monitor system initialized');
};

/**
 * 快捷键支持
 */
function setupMonitorShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Alt + M: 打开/关闭监控菜单
        if (e.altKey && e.key === 'm') {
            e.preventDefault();
            window.monitorController?.toggleMenu();
        }
        
        // Alt + 数字: 显示/隐藏特定监控
        if (e.altKey && e.key >= '1' && e.key <= '9') {
            const monitors = Array.from(window.monitorManager.monitors.keys());
            const index = parseInt(e.key) - 1;
            if (monitors[index]) {
                const monitorId = monitors[index];
                if (window.monitorManager.activeMonitors.has(monitorId)) {
                    window.monitorManager.hideMonitor(monitorId);
                } else {
                    window.monitorManager.showMonitor(monitorId);
                }
            }
        }
    });
}

/**
 * 便捷API - 快速显示监控
 */
window.showMonitor = function(monitorId) {
    window.monitorManager.showMonitor(monitorId);
};

window.hideMonitor = function(monitorId) {
    window.monitorManager.hideMonitor(monitorId);
};

window.toggleMonitor = function(monitorId) {
    if (window.monitorManager.activeMonitors.has(monitorId)) {
        window.monitorManager.hideMonitor(monitorId);
    } else {
        window.monitorManager.showMonitor(monitorId);
    }
};

window.addMonitorConfig = function(id, name, url) {
    window.monitorManager.addMonitor({
        id: id,
        name: name,
        url: url,
        width: 320,
        height: 180
    });
};

window.switchMonitorLayout = function(layoutMode) {
    window.monitorController?.switchLayout(layoutMode);
};

window.showAllMonitorsIn3D = function() {
     window.monitorController?.showAllIn3D();
 };

/**
 * 全局monitorControl对象 - 供Tool Action调用
 * 用于远程控制摄像头显示状态
 */
window.monitorControl = {
     /**
      * 显示指定摄像头
      * @param {string} cameraName - 摄像头名称 (e.g. 'JinLiLite1', 'ChiWen2')
      */
     showCamera(cameraName) {
         console.log(`[MonitorControl] Showing camera: ${cameraName}`);
         if (window.monitorManager) {
             window.monitorManager.showMonitor(cameraName);
             this.addMessage(`Showed camera: ${cameraName}`);
         }
     },
     
     /**
      * 隐藏指定摄像头
      * @param {string} cameraName - 摄像头名称
      */
     hideCamera(cameraName) {
         console.log(`[MonitorControl] Hiding camera: ${cameraName}`);
         if (window.monitorManager) {
             window.monitorManager.hideMonitor(cameraName);
             this.addMessage(`Hidden camera: ${cameraName}`);
         }
     },
     
     /**
      * 显示所有摄像头
      */
     showAllCameras() {
         console.log('[MonitorControl] Showing all cameras');
         if (window.monitorController) {
             window.monitorController.showAllMonitors();
         }
     },
     
     /**
      * 隐藏所有摄像头
      */
     hideAllCameras() {
         console.log('[MonitorControl] Hiding all cameras');
         if (window.monitorController) {
             window.monitorController.hideAllMonitors();
         }
     },
     
     /**
      * 放大/缩放摄像头 - 在3D场景中显示该摄像头
      * @param {string} cameraName - 摄像头名称
      */
     zoomCamera(cameraName) {
         console.log(`[MonitorControl] Zooming camera: ${cameraName}`);
         if (window.monitorManager) {
             // 首先确保摄像头可见
             window.monitorManager.showMonitor(cameraName);
             
             // 如果有3D集成，添加到3D场景中
             if (window.monitor3D && window.monitorManager.videoElements.has(cameraName)) {
                 const videoElement = window.monitorManager.videoElements.get(cameraName);
                 window.monitor3D.showMonitorIn3D(
                     cameraName,
                     videoElement,
                     window.monitorController?.currentLayout || 'ring',
                     0
                 );
             }
             
             this.addMessage(`Zoomed camera: ${cameraName}`);
         }
     },
     
     /**
      * 添加消息到聊天历史
      * @param {string} message - 消息内容
      */
     addMessage(message) {
         const chatHistory = document.getElementById('chat-history');
         if (!chatHistory) return;
         
         const messageEl = document.createElement('div');
         messageEl.className = 'message system';
         messageEl.innerHTML = `<div class="message-content">[CAMERA] ${message}</div>`;
         chatHistory.appendChild(messageEl);
         chatHistory.scrollTop = chatHistory.scrollHeight;
     }
 };
