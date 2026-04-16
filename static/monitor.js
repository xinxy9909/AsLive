// --- 监控视频管理模块 ---

/**
 * 监控视频配置
 * @typedef {Object} MonitorConfig
 * @property {string} id - 监控ID
 * @property {string} name - 监控名称
 * @property {string} url - 视频流URL (HLS M3U8)
 * @property {number} [width=320] - 显示宽度
 * @property {number} [height=180] - 显示高度
 * @property {boolean} [enabled=true] - 是否启用
 */

class MonitorManager {
    constructor() {
        // 监控配置映射
        this.monitors = new Map();
        this.videoElements = new Map();
        this.players = new Map();
        this.activeMonitors = new Set();
        
        // 容器引用
        this.container = null;
        this.hlsScript = null;
        
        // 初始化HLS.js库（用于跨浏览器HLS支持）
        this.initHLSLibrary();
    }
    
    /**
     * 初始化HLS.js库
     */
    initHLSLibrary() {
        if (!window.HLS) {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/hls.js@1.4.12/dist/hls.min.js';
            script.async = true;
            document.head.appendChild(script);
            this.hlsScript = script;
        }
    }
    
    /**
     * 初始化监控面板容器
     */
    initContainer() {
        if (!document.getElementById('monitors-container')) {
            const container = document.createElement('div');
            container.id = 'monitors-container';
            container.className = 'monitors-container';
            document.getElementById('ui-layer').appendChild(container);
            this.container = container;
        } else {
            this.container = document.getElementById('monitors-container');
        }
    }
    
    /**
     * 添加监控
     * @param {MonitorConfig} config 
     */
    addMonitor(config) {
        if (!config.id || !config.url) {
            console.error('Monitor config must have id and url');
            return false;
        }
        
        const defaultConfig = {
            name: config.name || `Monitor ${config.id}`,
            width: 320,
            height: 180,
            enabled: true,
            ...config
        };
        
        this.monitors.set(config.id, defaultConfig);
        return true;
    }
    
    /**
     * 创建监控面板元素
     * @param {string} monitorId 
     * @returns {HTMLElement}
     */
    createMonitorPanel(monitorId) {
        const config = this.monitors.get(monitorId);
        if (!config) {
            console.error(`Monitor ${monitorId} not found`);
            return null;
        }
        
        const panel = document.createElement('div');
        panel.id = `monitor-${monitorId}`;
        panel.className = 'monitor-panel';
        panel.style.width = `${config.width}px`;
        
        // 四个角落装饰
        const corners = ['tl', 'tr', 'bl', 'br'];
        corners.forEach(pos => {
            const corner = document.createElement('div');
            corner.className = `monitor-corner ${pos}`;
            panel.appendChild(corner);
        });
        
        // 视频容器
        const videoContainer = document.createElement('div');
        videoContainer.className = 'monitor-video-container';
        
        // 视频元素
        const video = document.createElement('video');
        video.id = `video-${monitorId}`;
        video.className = 'monitor-video';
        video.playsInline = true;
        video.muted = true;
        
        // 加载动画
        const loadingEl = document.createElement('div');
        loadingEl.className = 'monitor-loading';
        loadingEl.id = `loading-${monitorId}`;
        loadingEl.innerHTML = `
            <div class="loading-dots">
                <span></span><span></span><span></span>
            </div>
            <div class="loading-text">CONNECTING</div>
        `;
        loadingEl.style.display = 'none';
        
        videoContainer.appendChild(video);
        videoContainer.appendChild(loadingEl);
        panel.appendChild(videoContainer);
        
        // 顶部信息栏
        const infoBar = document.createElement('div');
        infoBar.className = 'monitor-info-bar';
        
        // 左侧: 图标 + ID + 名称
        const infoLeft = document.createElement('div');
        infoLeft.className = 'monitor-info-left';
        
        const iconEl = document.createElement('div');
        iconEl.className = 'monitor-icon';
        
        const idEl = document.createElement('span');
        idEl.className = 'monitor-id';
        idEl.textContent = monitorId.toUpperCase();
        
        const nameEl = document.createElement('span');
        nameEl.className = 'monitor-name';
        nameEl.textContent = config.name;
        
        infoLeft.appendChild(iconEl);
        infoLeft.appendChild(idEl);
        infoLeft.appendChild(nameEl);
        infoBar.appendChild(infoLeft);
        
        // 右侧: 按钮组
        const infoRight = document.createElement('div');
        infoRight.className = 'monitor-info-right';
        
        // 播放/暂停按钮
        const playBtn = document.createElement('button');
        playBtn.className = 'monitor-btn play-btn';
        playBtn.innerHTML = '<i class="fas fa-play"></i>';
        playBtn.title = 'Play/Pause';
        playBtn.onclick = (e) => {
            e.stopPropagation();
            this.togglePlay(monitorId);
        };
        
        // 静音按钮
        const muteBtn = document.createElement('button');
        muteBtn.className = 'monitor-btn mute-btn active';
        muteBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
        muteBtn.title = 'Mute/Unmute';
        muteBtn.onclick = (e) => {
            e.stopPropagation();
            this.toggleMute(monitorId);
        };
        
        // 全屏按钮
        const fullscreenBtn = document.createElement('button');
        fullscreenBtn.className = 'monitor-btn fullscreen-btn';
        fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
        fullscreenBtn.title = 'Fullscreen';
        fullscreenBtn.onclick = (e) => {
            e.stopPropagation();
            this.toggleFullscreen(monitorId);
        };
        
        // 关闭按钮
        const closeBtn = document.createElement('button');
        closeBtn.className = 'monitor-btn close-btn';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.title = 'Close Monitor';
        closeBtn.onclick = (e) => {
            e.stopPropagation();
            this.hideMonitor(monitorId);
        };
        
        infoRight.appendChild(playBtn);
        infoRight.appendChild(muteBtn);
        infoRight.appendChild(fullscreenBtn);
        infoRight.appendChild(closeBtn);
        infoBar.appendChild(infoRight);
        
        panel.appendChild(infoBar);
        
        // 底部状态栏
        const statusBar = document.createElement('div');
        statusBar.className = 'monitor-status-bar';
        
        // 状态指示器
        const statusEl = document.createElement('div');
        statusEl.className = 'monitor-status status-offline';
        statusEl.id = `status-${monitorId}`;
        statusEl.textContent = 'OFFLINE';
        
        // 时间戳
        const timestampEl = document.createElement('div');
        timestampEl.className = 'monitor-timestamp';
        timestampEl.id = `timestamp-${monitorId}`;
        timestampEl.textContent = '--:--:--';
        
        statusBar.appendChild(statusEl);
        statusBar.appendChild(timestampEl);
        panel.appendChild(statusBar);
        
        // 保存视频元素引用
        this.videoElements.set(monitorId, video);
        
        return panel;
    }
    
    /**
     * 显示监控
     * @param {string} monitorId 
     */
    showMonitor(monitorId) {
        if (!this.container) {
            this.initContainer();
        }
        
        if (this.activeMonitors.has(monitorId)) {
            return;
        }
        
        const panel = this.createMonitorPanel(monitorId);
        if (!panel) return;
        
        this.container.appendChild(panel);
        this.activeMonitors.add(monitorId);
        
        // 初始化视频播放
        setTimeout(() => {
            this.initializeMonitor(monitorId);
        }, 100);
    }
    
    /**
     * 初始化监控视频播放
     * @param {string} monitorId 
     */
    initializeMonitor(monitorId) {
        const video = this.videoElements.get(monitorId);
        const config = this.monitors.get(monitorId);
        
        if (!video || !config) return;
        
        video.addEventListener('loadstart', () => this.setStatus(monitorId, 'LOADING'));
        video.addEventListener('loadeddata', () => this.setStatus(monitorId, 'ONLINE'));
        video.addEventListener('error', () => this.setStatus(monitorId, 'ERROR'));
        video.addEventListener('stalled', () => this.setStatus(monitorId, 'STALLED'));
        
        if (window.HLS && HLS.isSupported()) {
            const hls = new HLS({
                enableWorker: true,
                lowLatencyMode: true,
                maxBufferLength: 5,
                testOnLoad: false
            });
            
            hls.loadSource(config.url);
            hls.attachMedia(video);
            
            hls.on(HLS.Events.MANIFEST_PARSED, () => {
                video.play().catch(err => {
                    console.warn(`Auto-play failed for ${monitorId}:`, err);
                });
            });
            
            hls.on(HLS.Events.ERROR, (event, data) => {
                console.error(`HLS error for ${monitorId}:`, data);
                this.setStatus(monitorId, 'ERROR');
            });
            
            this.players.set(monitorId, hls);
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
            video.src = config.url;
            video.play().catch(err => {
                console.warn(`Auto-play failed for ${monitorId}:`, err);
            });
        }
    }
    
    /**
     * 隐藏监控
     * @param {string} monitorId 
     */
    hideMonitor(monitorId) {
        if (!this.activeMonitors.has(monitorId)) {
            return;
        }
        
        // 停止播放
        const video = this.videoElements.get(monitorId);
        if (video) {
            video.pause();
        }
        
        // 清理HLS播放器
        const player = this.players.get(monitorId);
        if (player) {
            player.destroy();
            this.players.delete(monitorId);
        }
        
        // 移除DOM元素
        const panel = document.getElementById(`monitor-${monitorId}`);
        if (panel) {
            panel.remove();
        }
        
        this.activeMonitors.delete(monitorId);
    }
    
    /**
     * 切换播放/暂停
     * @param {string} monitorId 
     */
    togglePlay(monitorId) {
        const video = this.videoElements.get(monitorId);
        if (!video) return;
        
        if (video.paused) {
            video.play().catch(err => console.warn('Play failed:', err));
        } else {
            video.pause();
        }
        
        this.updatePlayButton(monitorId);
    }
    
    /**
     * 更新播放按钮状态
     * @param {string} monitorId 
     */
    updatePlayButton(monitorId) {
        const video = this.videoElements.get(monitorId);
        const panel = document.getElementById(`monitor-${monitorId}`);
        if (!panel) return;
        
        const playBtn = panel.querySelector('.play-btn');
        if (!playBtn) return;
        
        playBtn.innerHTML = video?.paused ? 
            '<i class="fas fa-play"></i>' : 
            '<i class="fas fa-pause"></i>';
    }
    
    /**
     * 设置监控状态
     * @param {string} monitorId 
     * @param {string} status 
     */
    setStatus(monitorId, status) {
        const statusEl = document.getElementById(`status-${monitorId}`);
        if (statusEl) {
            statusEl.textContent = status;
            statusEl.className = `monitor-status status-${status.toLowerCase()}`;
        }
        
        const timestampEl = document.getElementById(`timestamp-${monitorId}`);
        if (timestampEl) {
            const now = new Date();
            timestampEl.textContent = now.toTimeString().split(' ')[0];
        }
        
        const loadingEl = document.getElementById(`loading-${monitorId}`);
        if (loadingEl) {
            loadingEl.style.display = status === 'LOADING' ? 'flex' : 'none';
        }
    }
    
    /**
     * 切换静音
     * @param {string} monitorId 
     */
    toggleMute(monitorId) {
        const video = this.videoElements.get(monitorId);
        if (!video) return;
        
        video.muted = !video.muted;
        
        const panel = document.getElementById(`monitor-${monitorId}`);
        if (!panel) return;
        
        const muteBtn = panel.querySelector('.mute-btn');
        if (muteBtn) {
            muteBtn.innerHTML = video.muted ? 
                '<i class="fas fa-volume-mute"></i>' : 
                '<i class="fas fa-volume-up"></i>';
            muteBtn.classList.toggle('active', video.muted);
        }
    }
    
    /**
     * 切换全屏
     * @param {string} monitorId 
     */
    toggleFullscreen(monitorId) {
        const video = this.videoElements.get(monitorId);
        if (!video) return;
        
        const panel = document.getElementById(`monitor-${monitorId}`);
        if (!panel) return;
        
        if (document.fullscreenElement) {
            document.exitFullscreen();
            panel.querySelector('.fullscreen-btn').innerHTML = '<i class="fas fa-expand"></i>';
        } else {
            panel.requestFullscreen().then(() => {
                panel.querySelector('.fullscreen-btn').innerHTML = '<i class="fas fa-compress"></i>';
            }).catch(err => {
                console.warn('Fullscreen failed:', err);
            });
        }
    }
    
    /**
     * 显示缓冲指示器
     * @param {string} monitorId 
     */
    showBuffering(monitorId) {
        const bufferingEl = document.getElementById(`buffering-${monitorId}`);
        if (bufferingEl) {
            bufferingEl.style.display = 'flex';
        }
    }
    
    /**
     * 隐藏缓冲指示器
     * @param {string} monitorId 
     */
    hideBuffering(monitorId) {
        const bufferingEl = document.getElementById(`buffering-${monitorId}`);
        if (bufferingEl) {
            bufferingEl.style.display = 'none';
        }
    }
    
    /**
     * 获取所有活跃监控
     * @returns {Set<string>}
     */
    getActiveMonitors() {
        return new Set(this.activeMonitors);
    }
    
    /**
     * 隐藏所有监控
     */
    hideAllMonitors() {
        const monitors = Array.from(this.activeMonitors);
        monitors.forEach(id => this.hideMonitor(id));
    }
    
    /**
     * 显示所有已配置的监控
     */
    showAllMonitors() {
        this.monitors.forEach((config, id) => {
            if (config.enabled) {
                this.showMonitor(id);
            }
        });
    }
    
    /**
     * 获取监控配置
     * @param {string} monitorId 
     * @returns {MonitorConfig|null}
     */
    getMonitorConfig(monitorId) {
        return this.monitors.get(monitorId) || null;
    }
    
    /**
     * 获取所有监控配置
     * @returns {Map<string, MonitorConfig>}
     */
    getAllMonitors() {
        return new Map(this.monitors);
    }
}

// 创建全局管理器实例
window.monitorManager = new MonitorManager();
