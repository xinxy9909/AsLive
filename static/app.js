// --- 1. THREE.JS SCENE ---
let scene, camera, renderer, sphere, count, originalPositions;

function init3D() {
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x030303, 0.002);

    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 35;

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    document.getElementById('canvas-container').appendChild(renderer.domElement);

    // Particle Sphere
    const geometry = new THREE.SphereGeometry(12, 128, 128);
    const material = new THREE.PointsMaterial({
        size: 0.15,
        color: 0xffffff,
        transparent: true,
        opacity: 0.6,
        blending: THREE.AdditiveBlending,
        vertexColors: true
    });

    count = geometry.attributes.position.count;
    const colors = [];
    const color1 = new THREE.Color(0x00f2ff); // Cyan
    const color2 = new THREE.Color(0xbd00ff); // Purple
    originalPositions = geometry.attributes.position.array.slice();

    for (let i = 0; i < count; i++) {
        const mixed = color1.clone().lerp(color2, Math.random());
        colors.push(mixed.r, mixed.g, mixed.b);
    }
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    sphere = new THREE.Points(geometry, material);
    scene.add(sphere);
}

// --- 2. AUDIO & VISUALIZER ---
let audioContext, analyser, dataArray;
let micAnalyser, micDataArray;
let isAudioInit = false;
let smoothedBass = 0;
let smoothedAvg = 0;

const monitorCanvas = document.getElementById('mini-monitor');
const monitorCtx = monitorCanvas.getContext('2d');

function initAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.8;
        dataArray = new Uint8Array(analyser.frequencyBinCount);
        
        micAnalyser = audioContext.createAnalyser();
        micAnalyser.fftSize = 256;
        micAnalyser.smoothingTimeConstant = 0.8;
        micDataArray = new Uint8Array(micAnalyser.frequencyBinCount);
        
        isAudioInit = true;
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
}

// --- 3. LOGIC & INTERACTION ---
const recordBtn = document.getElementById('record-btn');
const textInput = document.getElementById('text-input');
const sendBtn = document.getElementById('send-btn');
const chatHistory = document.getElementById('chat-history');
const statusDisplay = document.getElementById('status-display');
const audioPlayer = document.getElementById('audio-player');
const clearHistoryBtn = document.getElementById('clear-history');

// 录音相关
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let isAlwaysListening = false; // 持续监听模式
let silenceStartTime = null;
const SILENCE_THRESHOLD = 15; // 静音阈值 (根据实际环境调整)
const SILENCE_DURATION = 1000; // 静音持续时间 (ms)

// 开启录音函数
async function startRecording() {
    if (isRecording) return;
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
        
        mediaRecorder.onstop = async () => {
            // 停止麦克风流的所有轨道
            stream.getTracks().forEach(track => track.stop());

            await interruptCurrent(); // 打断当前回复

            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            setStatus('UPLOADING...', 'busy');

            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.wav');

            try {
                const response = await fetch('/audio', {
                    method: 'POST',
                    body: formData
                });
                handleStream(response);
            } catch (e) {
                console.error(e);
                setStatus('ERROR', 'busy');
            }
        };
        
        mediaRecorder.start();
        isRecording = true;
        recordBtn.classList.add('recording');
        setStatus('LISTENING...', 'busy');
        silenceStartTime = null; 
        
        // 连接可视化
        initAudioContext();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(micAnalyser); 
        
    } catch (e) {
        console.error('Mic error:', e);
        alert('无法访问麦克风');
        isAlwaysListening = false;
        recordBtn.classList.remove('active');
    }
}

// 停止录音函数
function stopRecording() {
    if (isRecording && mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        isRecording = false;
        recordBtn.classList.remove('recording');
        silenceStartTime = null;
    }
}

// 音频播放队列
let audioQueue = [];
let isPlaying = false;
let currentAudioSource = null; // 用于 WebAudio 连接

// 当前 SSE 流的 reader，用于打断
let currentReader = null;

// 代次计数器：每次打断递增，旧 handleStream 检测到不匹配后不再推送音频
let streamGeneration = 0;

// 打断当前回复：取消 SSE 流、清空音频队列、停止播放
async function interruptCurrent() {
    streamGeneration++;   // 递增代次，旧 handleStream 的推送全部作废
    audioQueue = [];
    isPlaying = false;
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    audioPlayer.removeAttribute('src');
    audioPlayer.load();

    if (currentReader) {
        try { await currentReader.cancel(); } catch (_) {}
        currentReader = null;
    }
}

// 状态更新
function setStatus(status, type = 'normal') {
    statusDisplay.textContent = status;
    const dot = document.querySelector('.status-dot');
    dot.className = 'status-dot ' + (type === 'busy' ? 'busy' : 'healthy');
}

// 消息展示（仅用于用户消息和带初始内容的消息）
function addMessage(role, content) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    
    // 使用 marked 将 Markdown 转换为 HTML
    let htmlContent = content;
    try {
        // 配置 marked 选项
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true
            });
            htmlContent = marked.parse(content);
        }
    } catch (e) {
        console.warn('Markdown parsing error:', e);
        // 如果解析失败，使用原始内容
        htmlContent = content;
    }
    
    div.innerHTML = `
        <div class="role-label">${role === 'user' ? 'USER' : 'AI CORE'}</div>
        <div class="message-content markdown">${htmlContent}</div>
    `;
    
    // 应用代码高亮
    div.querySelectorAll('pre code').forEach((block) => {
        if (typeof hljs !== 'undefined') {
            hljs.highlightElement(block);
        }
    });
    
    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return div;
}

// 播放音频队列
async function playNextAudio() {
    if (audioQueue.length === 0) {
        isPlaying = false;
        setStatus('WAITING FOR INPUT...');
        
        // --- 持续监听模式的关键点 ---
        if (isAlwaysListening) {
            console.log("Continuous Mode: Playback finished, restarting listener...");
            setTimeout(startRecording, 500); // 稍微延迟一下，避免回音干扰
        }
        return;
    }

    isPlaying = true;
    const audioData = audioQueue.shift();
    const url = audioData.url;
    
    // 连接到 WebAudio 以驱动可视化
    initAudioContext();
    
    audioPlayer.src = url;
    audioPlayer.crossOrigin = "anonymous";
    
    // 等待加载
    await new Promise((resolve) => {
        audioPlayer.oncanplaythrough = resolve;
    });

    // 创建源并连接
    if (!currentAudioSource) {
        try {
            const source = audioContext.createMediaElementSource(audioPlayer);
            source.connect(analyser);
            analyser.connect(audioContext.destination);
            currentAudioSource = source; 
        } catch (e) {
            // ignore if already connected
        }
    }
    
    audioPlayer.play();
    setStatus('SPEAKING...', 'busy');

    audioPlayer.onended = () => {
        playNextAudio();
    };
}

// 处理 SSE 流
async function handleStream(response) {
     const reader = response.body.getReader();
     currentReader = reader;
     const myGen = streamGeneration;
     const decoder = new TextDecoder();
  
      const assistantMsgEl = document.createElement('div');
      assistantMsgEl.className = 'message assistant';
      assistantMsgEl.innerHTML = `
          <div class="role-label">AI CORE</div>
          <div class="message-content markdown"></div>
      `;
      chatHistory.appendChild(assistantMsgEl);
      chatHistory.scrollTop = chatHistory.scrollHeight;
      
       // 存储完整的消息文本，用于实时 Markdown 渲染
       let fullMessage = '';
       const contentDiv = assistantMsgEl.querySelector('.message-content');
       let hasContent = false;  // 标记是否收到了任何内容
       let renderTimeout; // 用于防抖渲染
       
       // 实时渲染 Markdown 的辅助函数（带防抖）
       function renderMarkdownIncremental() {
           if (renderTimeout) clearTimeout(renderTimeout);
           renderTimeout = setTimeout(() => {
               if (!fullMessage) return;
               try {
                   if (typeof marked !== 'undefined') {
                       marked.setOptions({
                           breaks: true,
                           gfm: true
                       });
                       const htmlContent = marked.parse(fullMessage);
                       contentDiv.innerHTML = htmlContent;
                       
                       // 应用代码高亮
                       contentDiv.querySelectorAll('pre code').forEach((block) => {
                           try {
                               if (typeof hljs !== 'undefined') {
                                   hljs.highlightElement(block);
                               }
                           } catch (highlightError) {
                               console.warn('Code highlight error:', highlightError);
                           }
                       });
                   } else {
                       contentDiv.textContent = fullMessage;
                   }
               } catch (e) {
                   console.warn('Markdown rendering error:', e);
                   contentDiv.textContent = fullMessage;
               }
               chatHistory.scrollTop = chatHistory.scrollHeight;
           }, 100); // 100ms 防抖延迟
       }
    
       while (true) {
           let done, value;
           try {
                ({ done, value } = await reader.read());
           } catch (_) {
                break;
           }
           if (done) break;
    
           if (myGen !== streamGeneration) break;
    
           const chunk = decoder.decode(value);
           const lines = chunk.split('\n\n');
    
           for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
    
                        if (data.type === 'start') {
                            setStatus('PROCESSING...', 'busy');
                        } else if (data.type === 'text') {
                            fullMessage += data.content;
                            hasContent = true;
                            // 实时增量渲染 Markdown
                            renderMarkdownIncremental();
                        } else if (data.type === 'audio') {
                            if (myGen === streamGeneration) {
                                audioQueue.push(data);
                                if (!isPlaying) {
                                    playNextAudio();
                                }
                            }
                        } else if (data.type === 'asr') {
                            addMessage('user', data.text);
                        } else if (data.type === 'tool_action') {
                            handleToolAction(data);
                        } else if (data.type === 'end') {
                            // 流结束，确保最后一次渲染完成
                            if (renderTimeout) clearTimeout(renderTimeout);
                            if (hasContent && fullMessage) {
                                try {
                                    if (typeof marked !== 'undefined') {
                                        marked.setOptions({
                                            breaks: true,
                                            gfm: true
                                        });
                                        const htmlContent = marked.parse(fullMessage);
                                        contentDiv.innerHTML = htmlContent;
                                        
                                        // 应用代码高亮
                                        contentDiv.querySelectorAll('pre code').forEach((block) => {
                                            try {
                                                if (typeof hljs !== 'undefined') {
                                                    hljs.highlightElement(block);
                                                }
                                            } catch (highlightError) {
                                                console.warn('Code highlight error:', highlightError);
                                            }
                                        });
                                    } else {
                                        console.warn('marked library not loaded, using plain text');
                                        contentDiv.textContent = fullMessage;
                                    }
                                } catch (e) {
                                    console.warn('Markdown rendering error:', e);
                                    contentDiv.textContent = fullMessage;
                                }
                            }
                        }
                    } catch (e) {
                        console.error('Parse error:', e);
                    }
                }
           }
       }
       if (currentReader === reader) currentReader = null;
  }

/**
 * 处理工具动作事件 - 更新前端UI
 */
function handleToolAction(toolAction) {
     const { tool_name, tool_input, tool_result } = toolAction;
     
     if (tool_result.status !== 'success') {
          console.warn(`Tool execution failed: ${tool_result.error || 'unknown error'}`);
          return;
     }
     
     if (tool_name === 'show_camera' || tool_name === 'hide_camera' || tool_name === 'zoom_camera') {
          handleSingleCameraAction(tool_name, tool_result.data);
     } else if (tool_name === 'show_all_cameras') {
          handleMultipleCamerasAction('show', tool_result.data);
     } else if (tool_name === 'hide_all_cameras') {
          handleMultipleCamerasAction('hide', tool_result.data);
     }
 }

/**
 * 处理单个摄像头的操作
 */
function handleSingleCameraAction(action, cameraData) {
     if (!cameraData || !cameraData.camera_name) {
          console.error('Invalid camera data:', cameraData);
          return;
     }
     
     const cameraName = cameraData.camera_name;
     const cameraUrl = cameraData.url;
     const zoomLevel = cameraData.zoom_level || 'normal';
     
     if (window.monitorManager && !window.monitorManager.monitors.has(cameraName)) {
          window.monitorManager.addMonitor({
               id: cameraName,
               name: cameraName,
               url: cameraUrl,
               width: 320,
               height: 180
          });
     }
     
      if (action === 'show_camera') {
           if (window.monitorManager) {
                window.monitorManager.showMonitor(cameraName);
                console.log(`[CAMERA] Showed camera: ${cameraName}`);
           }
      } else if (action === 'hide_camera') {
           if (window.monitorManager) {
                window.monitorManager.hideMonitor(cameraName);
                console.log(`[CAMERA] Hidden camera: ${cameraName}`);
           }
      } else if (action === 'zoom_camera') {
           if (window.monitorManager) {
                // 显示监控面板
                window.monitorManager.showMonitor(cameraName);
                
                // 根据 zoom_level 设置放大级别（使用 CSS 全屏，不需要用户手势）
                window.monitorManager.setZoomLevel(cameraName, zoomLevel);
                
                // 对于 large/medium 级别，在 3D 场景中显示
                if ((zoomLevel === 'large' || zoomLevel === 'medium') && 
                    window.monitor3D && window.monitorManager.videoElements.has(cameraName)) {
                    const videoElement = window.monitorManager.videoElements.get(cameraName);
                    window.monitor3D.showMonitorIn3D(
                        cameraName,
                        videoElement,
                        window.monitorController?.currentLayout || 'ring',
                        0
                    );
                }
                console.log(`[CAMERA] Zoomed camera: ${cameraName} (${zoomLevel})`);
           }
      }
}

/**
 * 处理多摄像头操作
 */
function handleMultipleCamerasAction(action, camerasData) {
     if (!Array.isArray(camerasData)) {
          console.error('Invalid cameras data:', camerasData);
          return;
     }
     
      camerasData.forEach(cameraData => {
           if (window.monitorManager && !window.monitorManager.monitors.has(cameraData.camera_name)) {
               window.monitorManager.addMonitor({
                   id: cameraData.camera_name,
                   name: cameraData.camera_name,
                   url: cameraData.url,
                   width: 320,
                   height: 180
               });
           }
           
           if (action === 'show' && window.monitorManager) {
               window.monitorManager.showMonitor(cameraData.camera_name);
           } else if (action === 'hide' && window.monitorManager) {
               window.monitorManager.hideMonitor(cameraData.camera_name);
           }
      });
      
      console.log(`[CAMERA] ${action === 'show' ? 'Showed' : 'Hidden'} ${camerasData.length} camera(s)`);
 }

// 发送文本
async function sendText() {
    const text = textInput.value.trim();
    if (!text) return;

    await interruptCurrent(); // 打断当前回复

    textInput.value = '';
    addMessage('user', text);
    setStatus('THINKING...', 'busy');

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        handleStream(response);
    } catch (e) {
        console.error(e);
        setStatus('ERROR', 'busy');
    }
}

// 录音逻辑
if (navigator.mediaDevices) {
    recordBtn.addEventListener('click', () => {
        if (!isAlwaysListening) {
            // 切换到持续监听模式
            isAlwaysListening = true;
            recordBtn.classList.add('active'); // CSS中可以增加一个 active 状态表示开启了循环
            const label = recordBtn.querySelector('.btn-label');
            if (label) label.textContent = 'ALWAYS LISTENING';
            startRecording();
        } else {
            // 关闭持续监听模式
            isAlwaysListening = false;
            recordBtn.classList.remove('active');
            const label = recordBtn.querySelector('.btn-label');
            if (label) label.textContent = 'TAP TO SPEAK';
            stopRecording();
        }
    });
}

// --- 4. ANIMATION LOOP ---
let time = 0;
let mouseX = 0, mouseY = 0;

document.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX - window.innerWidth / 2) * 0.0005;
    mouseY = (e.clientY - window.innerHeight / 2) * 0.0005;
});

function lerp(start, end, amt) {
    return (1 - amt) * start + amt * end;
}

function drawMonitor(data) {
    monitorCtx.clearRect(0, 0, monitorCanvas.width, monitorCanvas.height);
    monitorCtx.fillStyle = '#00f2ff';
    
    const barWidth = 3;
    const gap = 1;
    const step = Math.floor(data.length / (monitorCanvas.width / (barWidth + gap)));

    for (let i = 0; i < monitorCanvas.width; i += (barWidth + gap)) {
        const dataIndex = Math.floor(i / (barWidth + gap)) * step;
        const value = data[dataIndex] || 0;
        const percent = value / 255;
        const barHeight = percent * monitorCanvas.height;

        monitorCtx.globalAlpha = 0.5 + (percent * 0.5);
        monitorCtx.fillRect(i, monitorCanvas.height - barHeight, barWidth, barHeight);
    }
}

function drawIdleMonitor(t) {
    monitorCtx.clearRect(0, 0, monitorCanvas.width, monitorCanvas.height);
    monitorCtx.fillStyle = 'rgba(255, 255, 255, 0.1)';
    for (let i = 0; i < monitorCanvas.width; i += 4) {
        const h = 5 + Math.sin(i * 0.1 + t * 5) * 3;
        monitorCtx.fillRect(i, monitorCanvas.height - h, 3, h);
    }
}

function animate() {
    requestAnimationFrame(animate);
    time += 0.005;

    let bassTarget = 0;
    let avgTarget = 0;
    let currentData = null;

    if (isAudioInit) {
        if (isRecording) {
            micAnalyser.getByteFrequencyData(micDataArray);
            currentData = micDataArray;
        } else {
            analyser.getByteFrequencyData(dataArray);
            currentData = dataArray;
        }

        const overallSum = currentData.reduce((a, b) => a + b, 0);
        avgTarget = overallSum / currentData.length;
        
        // VAD: 自动静音检测
        if (isRecording) {
            if (avgTarget < SILENCE_THRESHOLD) {
                if (!silenceStartTime) silenceStartTime = Date.now();
                if (Date.now() - silenceStartTime > SILENCE_DURATION) {
                    console.log("VAD: 1s silence detected, auto-stopping...");
                    stopRecording();
                }
            } else {
                silenceStartTime = null;
            }
        }

        bassTarget = currentData[5] / 255;
        drawMonitor(currentData);
    } else {
        drawIdleMonitor(time);
    }

    smoothedBass = lerp(smoothedBass, bassTarget, 0.08);
    smoothedAvg = lerp(smoothedAvg, avgTarget / 255, 0.1);

    if (sphere) {
        const scaleTarget = 1 + (smoothedBass * 0.3);
        sphere.scale.lerp(new THREE.Vector3(scaleTarget, scaleTarget, scaleTarget), 0.05);

        const positions = sphere.geometry.attributes.position.array;
        const audioForce = smoothedAvg * 5.0;

        for (let i = 0; i < count; i++) {
            const px = originalPositions[i * 3];
            const py = originalPositions[i * 3 + 1];
            const pz = originalPositions[i * 3 + 2];

            let noise = Math.sin(px * 0.4 + time * 2) * 
                        Math.cos(py * 0.3 + time * 1.5) * 
                        Math.sin(pz * 0.4 + time * 2.5);

            const displacement = 1 + (noise * 0.1) + (noise * audioForce * 0.25);

            positions[i * 3]     = px * displacement;
            positions[i * 3 + 1] = py * displacement;
            positions[i * 3 + 2] = pz * displacement;
        }
        sphere.geometry.attributes.position.needsUpdate = true;
        sphere.rotation.y += 0.001 + (smoothedAvg * 0.002);
        sphere.rotation.x += (mouseY - sphere.rotation.x) * 0.05;
        sphere.rotation.y += (mouseX - sphere.rotation.y) * 0.05;
    }

    try {
        renderer.render(scene, camera);
    } catch (error) {
        // Handle CORS and other rendering errors gracefully
        if (error.message.includes('SecurityError') || error.message.includes('cross-origin')) {
            console.warn('[CORS] Video texture CORS issue detected, rendering without 3D video:', error);
            // Disable 3D video textures for this frame
        } else {
            console.error('[Render] WebGL rendering error:', error);
        }
    }
}


// 初始化
try {
    init3D();
    
    setTimeout(() => {
        initializeMonitorSystem(scene);
        initializeMonitorConfig();
    }, 500);
    
    animate();
} catch (e) {
    console.error("3D Init Failed:", e);
}

console.log("App loaded, binding events...");

// 事件绑定
if (sendBtn) {
    sendBtn.addEventListener('click', () => {
        sendText();
    });
}

if (textInput) {
    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendText();
        }
    });
}

if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', async () => {
        await fetch('/history', { method: 'DELETE' });
        chatHistory.innerHTML = '';
        setStatus('HISTORY CLEARED');
    });
}

window.addEventListener('resize', () => {
    if (camera && renderer) {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }
});
