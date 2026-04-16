// --- 监控视频3D集成模块 ---

/**
 * 3D监控集成 - 支持将监控视频作为Three.js纹理显示在3D场景中
 */
class Monitor3DIntegration {
    constructor(scene) {
        this.scene = scene;
        this.videoTextures = new Map();
        this.displayModes = new Map(); // 存储每个监控的显示模式
        this.displays3D = new Map(); // 3D显示对象
        this.screenMeshes = new Map(); // 屏幕网格
        
        // 布局参数
        this.layoutConfig = {
            spacing: 8,
            screenWidth: 8,
            screenHeight: 4.5,
            sphereRadius: 12,
            startAngle: -Math.PI / 4
        };
    }
    
    /**
     * 创建视频纹理
     * @param {string} monitorId 
     * @param {HTMLVideoElement} videoElement 
     */
    createVideoTexture(monitorId, videoElement) {
        try {
            // 创建视频纹理
            const texture = new THREE.VideoTexture(videoElement);
            texture.colorSpace = THREE.SRGBColorSpace;
            texture.minFilter = THREE.LinearFilter;
            texture.magFilter = THREE.LinearFilter;
            texture.format = THREE.RGBFormat;
            
            // 存储纹理
            this.videoTextures.set(monitorId, texture);
            
            return texture;
        } catch (error) {
            console.error(`[Monitor3D] Failed to create texture for ${monitorId}:`, error);
            // Return a fallback placeholder texture
            return new THREE.MeshBasicMaterial({ color: 0x333333 });
        }
    }
    
    /**
     * 创建屏幕显示（球面投影）
     * @param {string} monitorId 
     * @param {HTMLVideoElement} videoElement 
     * @param {number} index - 监控索引（用于排列）
     */
    createSphericalDisplay(monitorId, videoElement, index = 0) {
        const texture = this.createVideoTexture(monitorId, videoElement);
        
        // 创建球面显示的着色器
        const material = new THREE.MeshBasicMaterial({
            map: texture,
            side: THREE.DoubleSide
        });
        
        // 创建屏幕网格（扁平矩形，贴在球面上）
        const geometry = new THREE.PlaneGeometry(4, 3);
        const mesh = new THREE.Mesh(geometry, material);
        
        // 计算位置（球面分布）
        const angle = this.layoutConfig.startAngle + (index * Math.PI * 0.4);
        const radius = this.layoutConfig.sphereRadius + 2;
        
        mesh.position.x = Math.cos(angle) * radius;
        mesh.position.y = 2 + (Math.sin(angle) * 1.5);
        mesh.position.z = Math.sin(angle) * radius;
        
        // 面向球心
        mesh.lookAt(0, 2, 0);
        
        this.scene.add(mesh);
        this.displays3D.set(monitorId, { type: 'spherical', mesh, material });
        this.screenMeshes.set(monitorId, mesh);
        this.displayModes.set(monitorId, 'spherical');
        
        return mesh;
    }
    
    /**
     * 创建固定屏幕显示（浮动屏幕）
     * @param {string} monitorId 
     * @param {HTMLVideoElement} videoElement 
     * @param {number} index 
     */
    createScreenDisplay(monitorId, videoElement, index = 0) {
        const texture = this.createVideoTexture(monitorId, videoElement);
        
        const material = new THREE.MeshBasicMaterial({
            map: texture,
            side: THREE.DoubleSide
        });
        
        const geometry = new THREE.PlaneGeometry(6, 4);
        const mesh = new THREE.Mesh(geometry, material);
        
        // 垂直堆叠显示
        const yOffset = 15 - (index * 5);
        const xOffset = -8 - (index * 0.5);
        
        mesh.position.set(xOffset, yOffset, -25);
        mesh.rotation.z = (Math.random() - 0.5) * 0.1; // 轻微旋转
        
        this.scene.add(mesh);
        this.displays3D.set(monitorId, { type: 'screen', mesh, material });
        this.screenMeshes.set(monitorId, mesh);
        this.displayModes.set(monitorId, 'screen');
        
        return mesh;
    }
    
    /**
     * 创建环形显示（围绕球体）
     * @param {string} monitorId 
     * @param {HTMLVideoElement} videoElement 
     * @param {number} index 
     * @param {number} totalCount 
     */
    createRingDisplay(monitorId, videoElement, index = 0, totalCount = 3) {
        const texture = this.createVideoTexture(monitorId, videoElement);
        
        const material = new THREE.MeshBasicMaterial({
            map: texture,
            side: THREE.DoubleSide
        });
        
        const geometry = new THREE.PlaneGeometry(4, 3);
        const mesh = new THREE.Mesh(geometry, material);
        
        // 环形排列
        const angle = (index / totalCount) * Math.PI * 2;
        const radius = this.layoutConfig.sphereRadius + 4;
        
        mesh.position.x = Math.cos(angle) * radius;
        mesh.position.y = 0;
        mesh.position.z = Math.sin(angle) * radius;
        
        // 面向球心
        mesh.lookAt(0, 0, 0);
        
        this.scene.add(mesh);
        this.displays3D.set(monitorId, { type: 'ring', mesh, material });
        this.screenMeshes.set(monitorId, mesh);
        this.displayModes.set(monitorId, 'ring');
        
        return mesh;
    }
    
    /**
     * 显示监控在3D场景中
     * @param {string} monitorId 
     * @param {HTMLVideoElement} videoElement 
     * @param {string} [displayMode='ring'] - 'spherical', 'screen', 'ring'
     * @param {number} [index=0] - 显示索引
     */
    showMonitorIn3D(monitorId, videoElement, displayMode = 'ring', index = 0) {
        // 先移除旧的显示
        this.removeMonitorFrom3D(monitorId);
        
        let mesh;
        
        switch (displayMode) {
            case 'spherical':
                mesh = this.createSphericalDisplay(monitorId, videoElement, index);
                break;
            case 'screen':
                mesh = this.createScreenDisplay(monitorId, videoElement, index);
                break;
            case 'ring':
            default:
                mesh = this.createRingDisplay(monitorId, videoElement, index, 3);
                break;
        }
        
        return mesh;
    }
    
    /**
     * 移除3D显示
     * @param {string} monitorId 
     */
    removeMonitorFrom3D(monitorId) {
        const mesh = this.screenMeshes.get(monitorId);
        if (mesh) {
            this.scene.remove(mesh);
            mesh.geometry.dispose();
            if (mesh.material) {
                if (mesh.material.map) {
                    mesh.material.map.dispose();
                }
                mesh.material.dispose();
            }
        }
        
        this.screenMeshes.delete(monitorId);
        this.displays3D.delete(monitorId);
        this.displayModes.delete(monitorId);
        
        // 释放纹理
        const texture = this.videoTextures.get(monitorId);
        if (texture) {
            texture.dispose();
            this.videoTextures.delete(monitorId);
        }
    }
    
    /**
     * 更新显示模式
     * @param {string} monitorId 
     * @param {string} newMode 
     * @param {HTMLVideoElement} videoElement 
     * @param {number} index 
     */
    switchDisplayMode(monitorId, newMode, videoElement, index = 0) {
        this.removeMonitorFrom3D(monitorId);
        this.showMonitorIn3D(monitorId, videoElement, newMode, index);
    }
    
    /**
     * 获取所有3D显示
     */
    getAll3DDisplays() {
        return new Map(this.displays3D);
    }
    
    /**
     * 隐藏所有3D显示
     */
    hideAll3D() {
        this.screenMeshes.forEach((mesh) => {
            mesh.visible = false;
        });
    }
    
    /**
     * 显示所有3D显示
     */
    showAll3D() {
        this.screenMeshes.forEach((mesh) => {
            mesh.visible = true;
        });
    }
    
    /**
     * 添加环境光和阴影支持
     */
    enhanceSceneLighting() {
        // 添加点光源用于突出3D监控
        const pointLight = new THREE.PointLight(0x00f2ff, 1, 100);
        pointLight.position.set(0, 15, 0);
        this.scene.add(pointLight);
        
        // 添加环境光
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
        this.scene.add(ambientLight);
    }
    
    /**
     * 创建监控布局编排（自动布局多个监控）
     * @param {Map<string, HTMLVideoElement>} monitorElements 
     * @param {string} [layoutMode='ring'] 
     */
    arrangeMonitorsLayout(monitorElements, layoutMode = 'ring') {
        const monitors = Array.from(monitorElements.entries());
        
        monitors.forEach(([ monitorId, videoElement ], index) => {
            this.showMonitorIn3D(
                monitorId,
                videoElement,
                layoutMode,
                index
            );
        });
    }
    
    /**
     * 创建动画效果 - 监控跟踪
     */
    addMonitorAnimation() {
        // 在主animate循环中调用此函数的返回值
        return {
            animate: (time) => {
                this.screenMeshes.forEach((mesh) => {
                    // 轻微的呼吸效果
                    const scale = 1 + Math.sin(time * 0.5) * 0.05;
                    mesh.scale.set(scale, scale, 1);
                    
                    // 环形轻微旋转
                    if (this.displayModes.get(mesh.userData.monitorId) === 'ring') {
                        const position = mesh.position;
                        const angle = Math.atan2(position.z, position.x) + time * 0.1;
                        const radius = Math.sqrt(position.x * position.x + position.z * position.z);
                        mesh.position.x = Math.cos(angle) * radius;
                        mesh.position.z = Math.sin(angle) * radius;
                    }
                });
            }
        };
    }
}

// 注意：在使用Monitor3DIntegration前，需要确保scene已被初始化
// 例如：window.monitor3D = new Monitor3DIntegration(scene);
