/**
 * CAMPUS.EXE V3.0 - CLIENT CLIENT-SIDE MANAGER (JAVASCRIPT)
 * Fully redesigned client logic. Integrates websocket commands, range sliders,
 * interactive D-pads, settings tabs, copy/download actions, and ChatGPT-style chat bubbles.
 */

class RobotDashboard {
    constructor() {
        // Resolve WebSocket address dynamically from the browser address bar
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.wsUrl = `${wsProtocol}//${window.location.hostname}:8765/phone`;
        
        this.socket = null;
        this.reconnectTimer = null;
        this.pingTimer = null;
        
        // Settings Active Tab cache
        this.activeTab = "general";
        
        // Servo Tracking State
        this.isServoOn = false;
        
        // Element references
        this.elements = {
            // Header & Overall State
            overallStatus: document.getElementById("overall-status-badge"),
            
            // Telemetry Dot Indicators
            dotEsp32: document.getElementById("dot-esp32"),
            textEsp32: document.getElementById("text-esp32"),
            dotGemini: document.getElementById("dot-gemini"),
            textGemini: document.getElementById("text-gemini"),
            dotWebsocket: document.getElementById("dot-websocket"),
            textWebsocket: document.getElementById("text-websocket"),
            textSpeaker: document.getElementById("text-speaker"),
            textPing: document.getElementById("text-ping"),
            textBattery: document.getElementById("text-battery"),
            
            // Interaction / Speech Input
            chatInput: document.getElementById("chat-input"),
            btnSend: document.getElementById("btn-send"),
            btnMic: document.getElementById("btn-mic"),
            micIcon: document.getElementById("mic-icon"),
            voiceStatus: document.getElementById("voice-status-text"),
            speakingState: document.getElementById("speaking-state-badge"),
            speakingDot: document.getElementById("speaking-state-dot"),
            responseBox: document.getElementById("live-response-box"),
            
            // Chat History
            historyList: document.getElementById("conversation-history-list"),
            
            // D-Pad Joysticks & Sliders
            btnUp: document.getElementById("ctrl-up"),
            btnDown: document.getElementById("ctrl-down"),
            btnLeft: document.getElementById("ctrl-left"),
            btnRight: document.getElementById("ctrl-right"),
            btnStop: document.getElementById("ctrl-stop"),
            sliderSpeed: document.getElementById("ctrl-speed-range"),
            txtSpeedValue: document.getElementById("speed-value"),
            sliderHead: document.getElementById("ctrl-head-range"),
            txtHeadAngle: document.getElementById("head-angle-value"),
            btnToggleServo: document.getElementById("btn-toggle-servo"),
            servoHandle: document.getElementById("servo-toggle-handle"),
            
            // QR Code Actions
            btnCopyLink: document.getElementById("btn-copy-link"),
            btnDownloadQr: document.getElementById("btn-download-qr"),
            qrUrlText: document.getElementById("qr-url-text"),
            qrImg: document.getElementById("portal-qr-img"),
            
            // General Settings reboot
            btnReboot: document.getElementById("btn-reboot-exec"),
            
            // Audio toggle (tab 2)
            btnToggleSpeaker: document.getElementById("btn-toggle-speaker"),
            speakerHandle: document.getElementById("speaker-toggle-handle")
        };
        
        // Audio Toggle state (defaults to Bluetooth)
        this.isEsp32AudioOn = false;
        
        // Voice speech recognizer
        this.recognition = null;
        this.isListening = false;
        
        // History cache
        this.history = [];
        
        this.init();
    }
    
    init() {
        console.log(`[DASHBOARD] Resolving WebSocket host path: ${this.wsUrl}`);
        
        // Dynamic Host IP replacement for the URL text badge
        if (this.elements.qrUrlText) {
            this.elements.qrUrlText.innerText = `http://${window.location.host}`;
        }
        
        this.initSpeechRecognition();
        this.setupEventListeners();
        this.connect();
    }
    
    connect() {
        if (this.socket) {
            this.socket.close();
        }
        
        this.socket = new WebSocket(this.wsUrl);
        this.socket.onopen = () => this.handleOpen();
        this.socket.onmessage = (event) => this.handleMessage(event);
        this.socket.onclose = () => this.handleClose();
        this.socket.onerror = (error) => this.handleError(error);
    }
    
    handleOpen() {
        console.log("[DASHBOARD] WebSocket connection active.");
        
        // Send registration message
        this.socket.send(JSON.stringify({ type: "register", client: "phone" }));
        
        // Set visual status indicators
        this.setIndicatorState(this.elements.dotWebsocket, this.elements.textWebsocket, true, "Active");
        this.updateOverallStatus(true);
        
        // Enable controller elements
        this.setInputDisabledState(false);
        
        // Start ping ticker
        this.startPingLoop();
    }
    
    handleClose() {
        console.log("[DASHBOARD] WebSocket connection closed. Attempting reconnect...");
        
        // Toggle indicators to offline
        this.setIndicatorState(this.elements.dotWebsocket, this.elements.textWebsocket, false, "Disconnected");
        this.setIndicatorState(this.elements.dotEsp32, this.elements.textEsp32, false, "Disconnected");
        this.updateOverallStatus(false);
        this.elements.textPing.innerText = "-- ms";
        
        // Disable controllers
        this.setInputDisabledState(true);
        
        // Stop ping ticker
        this.stopPingLoop();
        
        if (!this.reconnectTimer) {
            this.reconnectTimer = setTimeout(() => {
                this.reconnectTimer = null;
                this.connect();
            }, 3000);
        }
    }
    
    handleError(error) {
        console.error("[DASHBOARD ERROR] Socket error observed:", error);
    }
    
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            const msgType = data.type;
            
            switch (msgType) {
                case "initial_status":
                    this.handleInitialStatus(data);
                    break;
                case "robot_status":
                    this.handleRobotStatus(data);
                    break;
                case "robot_telemetry":
                    this.handleRobotTelemetry(data);
                    break;
                case "pong":
                    this.handlePong(data);
                    break;
                case "status":
                    this.handleSpeakingStatus(data);
                    break;
                case "response":
                    this.handleConversationResponse(data);
                    break;
                case "personality_status":
                    this.updatePersonalityUI(data.personality);
                    break;
                default:
                    console.log(`[DASHBOARD] Unrouted event:`, data);
            }
        } catch (e) {
            console.error("[DASHBOARD ERROR] Failed to parse message:", e);
        }
    }
    
    handleInitialStatus(data) {
        console.log("[DASHBOARD] Initial status load:", data);
        
        // Set initial Speaker and Robot connection
        this.elements.textSpeaker.innerText = data.speaker_selected || "Bluetooth";
        this.isEsp32AudioOn = (data.speaker_selected === "ESP32");
        this.updateToggleSwitchUI(this.elements.btnToggleSpeaker, this.elements.speakerHandle, this.isEsp32AudioOn);
        
        this.handleRobotStatus({ connected: data.robot_connected });
    }
    
    handleRobotStatus(data) {
        const isConnected = data.connected;
        this.setIndicatorState(
            this.elements.dotEsp32, 
            this.elements.textEsp32, 
            isConnected, 
            isConnected ? "Connected" : "Disconnected"
        );
    }
    
    handleRobotTelemetry(data) {
        if (data.voltage) {
            this.elements.textBattery.innerText = `${data.voltage}V`;
        }
    }
    
    handleSpeakingStatus(data) {
        const action = data.action;
        
        if (action === "speaking") {
            this.elements.speakingState.innerText = "Speaking";
            this.elements.speakingState.className = "text-[10px] font-bold uppercase tracking-wider text-primary animate-pulse";
            this.elements.speakingDot.className = "status-indicator active !bg-primary";
            
            if (data.text) {
                this.elements.responseBox.innerText = `"${data.text}"`;
            }
        } else if (action === "idle") {
            this.elements.speakingState.innerText = "IDLE";
            this.elements.speakingState.className = "text-[10px] font-bold uppercase tracking-wider text-slate-400";
            this.elements.speakingDot.className = "status-indicator active";
        }
    }
    
    handleConversationResponse(data) {
        this.appendHistoryItem(data.question, data.answer);
    }
    
    handlePong(data) {
        const latency = Date.now() - data.timestamp;
        this.elements.textPing.innerText = `${latency} ms`;
    }
    
    /* Speech-to-Text Setup */
    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.log("[DASHBOARD] Speech Recognition unsupported in this browser.");
            return;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-IN'; // Indian English accent layout
        
        this.recognition.onstart = () => {
            this.isListening = true;
            this.elements.btnMic.className = "w-12 h-12 bg-primary text-white rounded-lg flex items-center justify-center transition-colors active-press shadow-lg shadow-primary/20";
            this.elements.micIcon.innerText = "mic";
            this.elements.voiceStatus.innerText = "Listening... Speak now!";
        };
        
        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            
            if (interimTranscript) {
                this.elements.chatInput.value = interimTranscript;
                this.elements.voiceStatus.innerText = `Comprehending: ${interimTranscript}`;
            }
            
            if (finalTranscript) {
                this.elements.chatInput.value = finalTranscript;
                this.elements.voiceStatus.innerText = "Sending query...";
                this.socket.send(JSON.stringify({ type: "query", text: finalTranscript }));
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error("[DASHBOARD] Speech error:", event.error);
            this.elements.voiceStatus.innerText = `Error: ${event.error}`;
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.elements.btnMic.className = "w-12 h-12 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg flex items-center justify-center transition-colors active-press";
            this.elements.micIcon.innerText = "mic_off";
            this.elements.voiceStatus.innerText = "Microphone Ready";
        };
    }
    
    toggleSpeechRecognition() {
        if (!this.recognition) {
            alert("Mic Speech recognition is not supported in this browser. Please use Google Chrome.");
            return;
        }
        
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }
    
    /* Setup Handlers and UI click listeners */
    setupEventListeners() {
        // Send / Submit Chat actions
        this.elements.btnSend.addEventListener("click", () => this.sendQuery());
        this.elements.chatInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") this.sendQuery();
        });
        
        // Microphone toggle action
        this.elements.btnMic.addEventListener("click", () => this.toggleSpeechRecognition());
        
        // D-Pad Joysticks (Touch targets min 56px)
        this.bindDpadButton(this.elements.btnUp, "up");
        this.bindDpadButton(this.elements.btnDown, "down");
        this.bindDpadButton(this.elements.btnLeft, "left");
        this.bindDpadButton(this.elements.btnRight, "right");
        this.bindDpadButton(this.elements.btnStop, "stop");
        
        // Drive speed slider
        this.elements.sliderSpeed.addEventListener("input", (e) => {
            const val = e.target.value;
            this.elements.txtSpeedValue.innerText = `${val}%`;
            this.sendControlCommand({ speed: parseInt(val) });
        });
        
        // Head angle rotation slider
        this.elements.sliderHead.addEventListener("input", (e) => {
            const val = e.target.value;
            this.elements.txtHeadAngle.innerText = `${val}°`;
            this.sendControlCommand({ head: parseInt(val) });
        });
        
        // Servo Toggle switch
        this.elements.btnToggleServo.addEventListener("click", () => {
            this.isServoOn = !this.isServoOn;
            this.updateToggleSwitchUI(this.elements.btnToggleServo, this.elements.servoHandle, this.isServoOn);
            this.sendControlCommand({ servo: this.isServoOn });
        });
        
        // Settings Navigation Tabs swapping
        const tabButtons = document.querySelectorAll(".settings-tab-btn");
        tabButtons.forEach(btn => {
            btn.addEventListener("click", (e) => {
                const targetTab = btn.getAttribute("data-tab");
                this.switchSettingsTab(targetTab, btn);
            });
        });
        
        // Reboot trigger (tab 1)
        this.elements.btnReboot.addEventListener("click", () => {
            const isConfirmed = confirm("Are you sure you want to reboot the robot guide dashboard servers?");
            if (isConfirmed) {
                this.socket.send(JSON.stringify({ type: "control", command: "reboot" }));
            }
        });
        
        // Audio Toggle switch (tab 2)
        this.elements.btnToggleSpeaker.addEventListener("click", () => {
            this.isEsp32AudioOn = !this.isEsp32AudioOn;
            this.updateToggleSwitchUI(this.elements.btnToggleSpeaker, this.elements.speakerHandle, this.isEsp32AudioOn);
            const speaker = this.isEsp32AudioOn ? "ESP32" : "Bluetooth";
            this.socket.send(JSON.stringify({ type: "control", speaker_select: speaker }));
            this.elements.textSpeaker.innerText = speaker;
        });
        
        // QR Code copy action
        this.elements.btnCopyLink.addEventListener("click", () => {
            const copyText = `http://${window.location.host}`;
            navigator.clipboard.writeText(copyText).then(() => {
                alert("URL Link copied to clipboard!");
            }).catch(err => {
                console.error("Failed to copy URL:", err);
            });
        });
        
        // QR Code download action
        this.elements.btnDownloadQr.addEventListener("click", () => {
            const link = document.createElement("a");
            link.href = "/static/assets/qr_code.png";
            link.download = "robot_qr_code.png";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });

        // AI Personality Switcher Buttons
        const personaButtons = document.querySelectorAll(".personality-btn");
        personaButtons.forEach(btn => {
            btn.addEventListener("click", () => {
                const persona = btn.getAttribute("data-persona");
                this.selectPersonality(persona);
            });
        });
    }

    selectPersonality(persona) {
        if (navigator.vibrate) {
            navigator.vibrate(40);
        }
        this.sendControlCommand({ personality: persona });
        this.updatePersonalityUI(persona);
    }

    updatePersonalityUI(persona) {
        const badgeEl = document.getElementById("current-personality-badge");
        const personaButtons = document.querySelectorAll(".personality-btn");
        
        const labels = {
            "cute": "🌸 CUTE BESTIE",
            "savage": "💀 SAVAGE ROAST",
            "formal": "👔 FORMAL GUIDE",
            "entrepreneur": "💼 FOUNDER & ROI",
            "entertainer": "🎭 HYPE STAR",
            "consul": "💖 CARING CONSUL",
            "content_advisor": "📲 VIRAL ADVISOR"
        };
        
        if (badgeEl) {
            badgeEl.innerText = labels[persona] || persona.toUpperCase();
        }
        
        personaButtons.forEach(btn => {
            const p = btn.getAttribute("data-persona");
            if (p === persona) {
                btn.className = "personality-btn flex flex-col items-center justify-center gap-1 p-3 rounded-xl border border-primary/50 bg-primary/10 transition-all cursor-pointer opacity-100";
            } else {
                btn.className = "personality-btn flex flex-col items-center justify-center gap-1 p-3 rounded-xl border border-[#1f222d] bg-[#0e1014] hover:bg-[#14161d] transition-all cursor-pointer opacity-70";
            }
        });
    }
    
    bindDpadButton(buttonEl, command) {
        if (!buttonEl) return;
        
        const triggerVibration = () => {
            if (navigator.vibrate) {
                navigator.vibrate(35);
            }
        };

        const startDrive = (e) => {
            if (e) e.preventDefault();
            triggerVibration();
            this.sendControlCommand({ command: command });
        };

        const stopDrive = (e) => {
            if (e) e.preventDefault();
            // Automatically stop motors when releasing directional buttons
            if (command !== "stop") {
                this.sendControlCommand({ command: "stop" });
            }
        };

        // Touch & Mouse Press events
        buttonEl.addEventListener("mousedown", startDrive);
        buttonEl.addEventListener("touchstart", startDrive);

        // Touch & Mouse Release events (auto-stop safety)
        if (command !== "stop") {
            buttonEl.addEventListener("mouseup", stopDrive);
            buttonEl.addEventListener("mouseleave", stopDrive);
            buttonEl.addEventListener("touchend", stopDrive);
        }
    }
    
    sendQuery() {
        const queryText = this.elements.chatInput.value.trim();
        if (!queryText) return;
        
        this.socket.send(JSON.stringify({ type: "query", text: queryText }));
        this.elements.chatInput.value = "";
    }
    
    sendControlCommand(payload) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: "control",
                ...payload
            }));
        }
    }
    
    switchSettingsTab(tabName, clickedBtn) {
        this.activeTab = tabName;
        
        // Update active tab buttons styling
        document.querySelectorAll(".settings-tab-btn").forEach(btn => {
            btn.classList.remove("active", "text-primary", "border-b", "border-primary");
            btn.classList.add("text-slate-400");
        });
        
        clickedBtn.classList.remove("text-slate-400");
        clickedBtn.classList.add("active", "text-primary", "border-b", "border-primary");
        
        // Swap tab panel visibility
        document.querySelectorAll(".settings-tab-content").forEach(panel => {
            panel.classList.add("hidden");
        });
        
        const targetPanel = document.getElementById(`tab-${tabName}`);
        if (targetPanel) {
            targetPanel.classList.remove("hidden");
        }
    }
    
    updateToggleSwitchUI(btnEl, handleEl, isOn) {
        if (!btnEl || !handleEl) return;
        
        if (isOn) {
            btnEl.className = "w-12 h-6 bg-primary rounded-full relative border border-primary transition-colors";
            handleEl.className = "w-4 h-4 bg-white rounded-full absolute right-1 top-1/2 -translate-y-1/2 transition-all";
        } else {
            btnEl.className = "w-12 h-6 bg-slate-800 rounded-full relative border border-slate-700 transition-colors";
            handleEl.className = "w-4 h-4 bg-slate-400 rounded-full absolute left-1 top-1/2 -translate-y-1/2 transition-all";
        }
    }
    
    /* Telemetry State Visualisers */
    setIndicatorState(dotEl, textEl, isOnline, text) {
        if (!dotEl || !textEl) return;
        
        if (isOnline) {
            dotEl.className = "status-indicator active";
            textEl.innerText = text;
        } else {
            dotEl.className = "status-indicator inactive";
            textEl.innerText = text;
        }
    }
    
    updateOverallStatus(isRobotConnected) {
        if (!this.elements.overallStatus) return;
        
        if (isRobotConnected) {
            this.elements.overallStatus.className = "px-3 py-1 bg-tertiary/10 border border-tertiary/20 text-tertiary text-[10px] font-bold rounded-full uppercase";
            this.elements.overallStatus.innerText = "Online";
        } else {
            this.elements.overallStatus.className = "px-3 py-1 bg-primary/10 border border-primary/20 text-primary text-[10px] font-bold rounded-full uppercase";
            this.elements.overallStatus.innerText = "Offline";
        }
    }
    
    setInputDisabledState(isDisabled) {
        this.elements.chatInput.disabled = isDisabled;
        this.elements.btnSend.disabled = isDisabled;
        this.elements.btnMic.disabled = isDisabled;
        
        // Disable controllers
        this.elements.btnUp.disabled = isDisabled;
        this.elements.btnDown.disabled = isDisabled;
        this.elements.btnLeft.disabled = isDisabled;
        this.elements.btnRight.disabled = isDisabled;
        this.elements.btnStop.disabled = isDisabled;
        this.elements.sliderSpeed.disabled = isDisabled;
        this.elements.sliderHead.disabled = isDisabled;
        this.elements.btnToggleServo.disabled = isDisabled;
        
        this.elements.btnToggleSpeaker.disabled = isDisabled;
        
        if (isDisabled) {
            this.elements.voiceStatus.innerText = "WebSocket Disconnected";
        } else {
            this.elements.voiceStatus.innerText = "Microphone Ready";
        }
    }
    
    startPingLoop() {
        this.stopPingLoop();
        this.pingTimer = setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({
                    type: "ping",
                    timestamp: Date.now()
                }));
            }
        }, 3000);
    }
    
    stopPingLoop() {
        if (this.pingTimer) {
            clearInterval(this.pingTimer);
            this.pingTimer = null;
        }
    }
    
    appendHistoryItem(query, response) {
        if (!this.elements.historyList) return;
        
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        // Remove default welcome bubble placeholder on first real query entry
        const welcome = this.elements.historyList.querySelector(".chat-bubble-guide:first-child");
        if (welcome && this.history.length === 0) {
            this.elements.historyList.innerHTML = "";
        }
        
        // 1. Create User bubble (Align right, red fill)
        const userBubble = document.createElement("div");
        userBubble.className = "chat-bubble-user";
        userBubble.innerHTML = `
            <span class="text-[9px] text-slate-500 font-bold uppercase tracking-widest pr-1">USER</span>
            <div class="bubble-content">
                ${query}
            </div>
        `;
        
        // 2. Create Guide response bubble (Align left, dark surface)
        const isRoast = response.toLowerCase().includes("fresher") || response.toLowerCase().includes("bro");
        const guideBubble = document.createElement("div");
        guideBubble.className = `chat-bubble-guide ${isRoast ? 'roast' : ''}`;
        guideBubble.innerHTML = `
            <span class="text-[9px] text-slate-500 font-bold uppercase tracking-widest pl-1">CAMPUS.EXE</span>
            <div class="bubble-content">
                ${response}
            </div>
        `;
        
        // Append bubbles to container
        this.elements.historyList.appendChild(userBubble);
        this.elements.historyList.appendChild(guideBubble);
        
        // Smooth scroll to bottom on new additions
        this.elements.historyList.scrollTop = this.elements.historyList.scrollHeight;
        
        // Save to cache
        this.history.push({ query, response, time: timeStr });
    }
}

// Instantiate HMI controller when DOM loads
window.addEventListener("DOMContentLoaded", () => {
    window.dashboard = new RobotDashboard();
});
