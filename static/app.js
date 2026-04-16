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
let micAnalyser, micDataArray; // 分离麦克风分析器
let isAudioInit = false;
let smoothedBass = 0;
let smoothedAvg = 0;

// Mini Monitor
const monitorCanvas = document.getElementById('mini-monitor');
const monitorCtx = monitorCanvas.getContext('2d');

function initAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // 播放用的分析器 (连接到 Destination)
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        analyser.smoothingTimeConstant = 0.8;
        dataArray = new Uint8Array(analyser.frequencyBinCount);
        
        // 麦克风用的分析器 (不连接到 Destination)
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

// ... (Create initMicAudio helper if needed, but handled in record logic)

// 录音逻辑中:
// source.connect(micAnalyser); 

// 动画循环中:
// if (isRecording) { micAnalyser.getByteFrequencyData(micDataArray); ... use micDataArray }
// else if (isPlaying) { analyser.getByteFrequencyData(dataArray); ... use dataArray }

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
    // ⚠️ 全部同步操作必须在 await 之前完成。
    // await reader.cancel() 会让出事件循环，旧 handleStream 可能趁机推送音频。
    streamGeneration++;   // 递增代次，旧 handleStream 的推送全部作废
    audioQueue = [];
    isPlaying = false;
    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    audioPlayer.removeAttribute('src');
    audioPlayer.load();

    // SSE 流取消是异步操作，放在最后
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
    div.innerHTML = `
        <div class="role-label">${role === 'user' ? 'USER' : 'AI CORE'}</div>
        <div class="message-content">${content}</div>
    `;
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
        // fix: 只需要创建一次
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
     const myGen = streamGeneration; // 捕获本次代次
     const decoder = new TextDecoder();
 
     // 每次 handleStream 直接创建独立的消息元素，
     // 不依赖任何 DOM 全局状态，彻底杜绝消息混合。
     const assistantMsgEl = document.createElement('div');
     assistantMsgEl.className = 'message assistant';
     assistantMsgEl.innerHTML = `
         <div class="role-label">AI CORE</div>
         <div class="message-content"></div>
     `;
     chatHistory.appendChild(assistantMsgEl);
     chatHistory.scrollTop = chatHistory.scrollHeight;
 
     while (true) {
         let done, value;
         try {
             ({ done, value } = await reader.read());
         } catch (_) {
             break; // reader 被取消（打断）
         }
         if (done) break;
 
         // 代次不匹配说明已被打断，立即停止处理
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
                         const contentDiv = assistantMsgEl.querySelector('.message-content');
                         contentDiv.textContent += data.content;
                         chatHistory.scrollTop = chatHistory.scrollHeight;
                     } else if (data.type === 'audio') {
                         // 代次匹配才推送音频，防止旧流在 await 间隙塞入过期音频
                         if (myGen === streamGeneration) {
                             audioQueue.push(data);
                             if (!isPlaying) {
                                 playNextAudio();
                             }
                         }
                     } else if (data.type === 'asr') {
                         addMessage('user', data.text);
                     } else if (data.type === 'tool_action') {
                         // 处理Monitor Agent的工具执行结果
                         console.log('Tool action received:', data);
                         handleToolAction(data);
                     } else if (data.type === 'end') {
                         // 流结束，无需额外处理
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
     
     console.log(`Executing tool: ${tool_name}`, {input: tool_input, result: tool_result});
     
     // 更新监控器状态
     if (window.monitorControl) {
         if (tool_name === 'show_camera' && tool_input.camera_name) {
             window.monitorControl.showCamera(tool_input.camera_name);
         } else if (tool_name === 'hide_camera' && tool_input.camera_name) {
             window.monitorControl.hideCamera(tool_input.camera_name);
         } else if (tool_name === 'show_all_cameras') {
             window.monitorControl.showAllCameras();
         } else if (tool_name === 'hide_all_cameras') {
             window.monitorControl.hideAllCameras();
         } else if (tool_name === 'zoom_camera' && tool_input.camera_name) {
             window.monitorControl.zoomCamera(tool_input.camera_name);
         }
     }
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

    renderer.render(scene, camera);
}


// 初始化
try {
    console.log("Initializing 3D Scene...");
    init3D();
    
    // 初始化监控系统
    setTimeout(() => {
        console.log("Initializing Monitor System...");
        initializeMonitorSystem(scene);
        
        // 使用配置文件初始化监控
        initializeMonitorConfig();
        
        console.log("Monitor system initialized with config");
    }, 500);
    
    animate();
} catch (e) {
    console.error("3D Init Failed:", e);
    // 即使 3D 失败，也要让聊天可用
}

console.log("App loaded, binding events...");

// 事件绑定
if (sendBtn) {
    sendBtn.addEventListener('click', () => {
        console.log("Send button clicked");
        sendText();
    });
} else {
    console.error("Send button not found!");
}

if (textInput) {
    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            console.log("Enter key pressed");
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
