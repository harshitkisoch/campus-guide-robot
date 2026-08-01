# 🚀 Campus Guide Robot — Setup Guide (For New Contributors)

> **This guide walks you through everything you need to install and configure after cloning this repository on a fresh Windows laptop.**

---

## 📋 Prerequisites Checklist

Before you begin, make sure your laptop has:

| # | Requirement | Minimum Version | Download Link |
|---|-------------|-----------------|---------------|
| 1 | **Python** | 3.10 or higher | [python.org/downloads](https://www.python.org/downloads/) |
| 2 | **Git** | Any recent | [git-scm.com](https://git-scm.com/downloads) |
| 3 | **VS Code** | Latest | [code.visualstudio.com](https://code.visualstudio.com/) |
| 4 | **PlatformIO Extension** | Latest | Install from VS Code Extensions tab |
| 5 | **Google Chrome** | Latest | For phone dashboard testing |

> [!IMPORTANT]
> During Python installation, **check the box that says "Add Python to PATH"**. If you miss this, nothing will work from the terminal.

---

## 📥 Step 1: Clone the Repository

Open a terminal (PowerShell or CMD) and run:

```bash
git clone https://github.com/harshitkisoch/campus-guide-robot.git
cd campus-guide-robot
```

---

## 📂 Step 2: Create Missing Files & Folders

The following files are **excluded from Git** (via `.gitignore`) because they contain private credentials. You must create them manually.

### 2.1 — Create the `.env` file (Python secrets)

In the **root** of the project, create a file named `.env`:

```
campus-guide-robot/
├── .env              ← CREATE THIS FILE
├── .env.example      ← (use this as reference)
├── main.py
└── ...
```

Copy the contents from `.env.example` and fill in your own values:

```env
# Google Gemini API Configuration (Multi-Key Rotation Queue)
# Get FREE keys from: https://aistudio.google.com/
GEMINI_API_KEYS=key_1_here,key_2_here
GEMINI_MODEL=gemini-1.5-flash

# Sarvam AI API Key (For Hindi Speech Output - Priya Female Voice)
# Get key from: https://dashboard.sarvam.ai/
SARVAM_API_KEY=sk_your_sarvam_key_here

# Audio Output Channel ('sarvam' for Hindi, 'bluetooth' for Zira, or 'esp32' for SAM)
OUTPUT_DEVICE=sarvam

# Text-To-Speech Settings
TTS_RATE=160
TTS_VOLUME=1.0

# WebSocket Configuration (leave defaults)
WS_HOST=0.0.0.0
WS_PORT=8765
```

> [!TIP]
> **For detailed step-by-step instructions on finding keys & setting up NodeMCU wiring, see**:
> * 🔑 [API Keys & Quickstart Guide](file:///h:/campus%20guide%20robot/docs/API_KEYS_AND_QUICKSTART.md)
> * 🔌 [NodeMCU Hardware Wiring Guide](file:///h:/campus%20guide%20robot/docs/HARDWARE_WIRING_NODEMCU.md)

> [!CAUTION]
> **Never commit the `.env` file to GitHub!** It contains your private API key. The `.gitignore` already prevents this, but double-check.

### 2.2 — Create the ESP32 Wi-Fi credentials file

Navigate to `esp32/include/` and create a file named `wifi_credentials.h`:

```
campus-guide-robot/
├── esp32/
│   ├── include/
│   │   ├── wifi_credentials.h           ← CREATE THIS FILE
│   │   └── wifi_credentials.h.example   ← (use this as reference)
│   └── src/
│       └── main.cpp
```

Copy the contents from `wifi_credentials.h.example` and fill in your values:

```cpp
#ifndef WIFI_CREDENTIALS_H
#define WIFI_CREDENTIALS_H

// Replace with your Wi-Fi name and password
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"

// Your laptop's IP address on the local network
// Find it by running in terminal:
//   python -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0])"
#define WS_SERVER_IP "192.168.1.100"

#define WS_SERVER_PORT 8765

#endif
```

### 2.3 — Create the Python Virtual Environment folder

```powershell
python -m venv .venv
```

This creates a `.venv/` folder (also excluded from Git).

---

## 📦 Step 3: Install Python Dependencies

Activate the virtual environment and install packages:

```powershell
# Activate the virtual environment
.\.venv\Scripts\activate

# Install all required Python packages
pip install -r requirements.txt
```

This installs the following packages:

| Package | Version | Purpose |
|---------|---------|---------|
| `google-genai` | ≥0.1.1 | Google Gemini AI API client |
| `pydantic-settings` | ≥2.2.1 | Configuration validation |
| `pyttsx3` | ≥2.90 | Offline text-to-speech (Windows SAPI5) |
| `python-dotenv` | ≥1.0.1 | Load `.env` environment variables |
| `pyserial` | ≥3.5 | USB serial communication with ESP32 |
| `websockets` | ≥12.0 | WebSocket server for real-time communication |
| `qrcode` | ≥7.4.2 | QR code generation for mobile access |
| `pillow` | ≥10.0.0 | Image processing (QR code PNG export) |
| `zeroconf` | ≥0.132.0 | mDNS network discovery |

---

## 🔧 Step 4: Install PlatformIO (for ESP32 firmware)

1. Open **VS Code**.
2. Go to **Extensions** (Ctrl+Shift+X).
3. Search for **"PlatformIO IDE"** and click **Install**.
4. Wait for PlatformIO to finish its initial setup (it downloads toolchains automatically).
5. **Restart VS Code** after installation.

PlatformIO will automatically read the `platformio.ini` file and download the ESP32 Arduino framework and C++ library dependencies:
- `ESP8266Audio` (audio output)
- `ESP8266SAM` (speech synthesis)
- `ArduinoWebsockets` (WebSocket client)
- `ArduinoJson` (JSON parsing)

---

## 🔌 Step 5: Find Your Serial Port (ESP32)

1. Plug your ESP32 into the laptop via USB cable.
2. Open **Device Manager** → expand **Ports (COM & LPT)**.
3. Note the COM port number (e.g., `COM3`, `COM9`).
4. Update **two places**:
   - In `.env` file: `SERIAL_PORT=COM3`
   - In `platformio.ini` file: `upload_port = COM3`

> [!NOTE]
> If you don't see the COM port, you may need to install the **CP2102** or **CH340** USB driver for your ESP32 board.

---

## 🌐 Step 6: Find Your Laptop IP Address

Run this command in your terminal:

```powershell
python -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0])"
```

It will print something like `192.168.1.18`. Put this IP in:
- `esp32/include/wifi_credentials.h` → `WS_SERVER_IP`

---

## 🔥 Step 7: Windows Firewall Configuration

Windows Firewall blocks incoming connections by default. You must allow traffic on two ports:

1. Press **Win + R** → type `wf.msc` → press Enter.
2. Click **Inbound Rules** → **New Rule...**
3. Select **Port** → Next.
4. Select **TCP** → Specific local ports: `8000, 8765` → Next.
5. Select **Allow the connection** → Next → Next.
6. Name it: `Campus Guide Robot` → Finish.

---

## ✅ Step 8: Run the Project

```powershell
# Make sure virtual environment is activated
.\.venv\Scripts\activate

# Start the robot server
python main.py
```

You should see output like this:

```
--------------------------------------------
    CAMPUS GUIDE ROBOT - PHASE 1 CONVERSATION
--------------------------------------------
[PIPELINE] Initializing core modules...
[WEB SERVER] HTTP Server successfully running on: http://0.0.0.0:8000
[WS SERVER] Initialized central router for port 8765
[WS SERVER] Central WebSocket router active on ws://0.0.0.0:8765
[AUDIO] Local Bluetooth Audio driver initialized
[AUDIO MANAGER] Configured output channel: [BLUETOOTH]
[PIPELINE] Ready.
Type your questions below.
```

Then open **Chrome on your phone** and go to: `http://<YOUR_LAPTOP_IP>:8000`

---

## 📱 Step 9: Mobile Phone Microphone Fix

Chrome blocks microphone access on insecure HTTP connections. To fix this:

1. Open Chrome on your **phone**.
2. In the address bar, type: `chrome://flags`
3. Search for: `unsafely-treat-insecure-origin-as-secure`
4. Set it to **Enabled**.
5. In the text field, type: `http://<YOUR_LAPTOP_IP>:8000`
6. Tap **Relaunch**.

---

## 🔄 Step 10: Flash ESP32 Firmware (Optional)

If you have an ESP32 board and want to flash the robot firmware:

```powershell
# Using PlatformIO CLI
pio run --target upload

# Open Serial Monitor to see logs
pio device monitor --baud 115200
```

Or use the PlatformIO sidebar in VS Code → click **Upload** and **Serial Monitor**.

---

## 📁 Complete Folder Structure After Setup

```
campus-guide-robot/
│
├── .env                          ← CREATED BY YOU (secrets)
├── .env.example                  ← Template reference
├── .gitignore
├── .venv/                        ← CREATED BY YOU (virtual environment)
├── main.py                       ← Entry point
├── requirements.txt              ← Python dependencies
├── platformio.ini                ← ESP32 build config
│
├── brain/
│   └── gemini_client.py          ← Gemini AI client
│
├── core/
│   ├── main.py                   ← CLI REPL loop
│   └── pipeline.py               ← Central orchestrator
│
├── config/
│   ├── settings.py               ← Pydantic settings loader
│   └── robot_identity.py         ← Network identity & mDNS
│
├── audio/
│   ├── base_output.py            ← Abstract audio interface
│   ├── bluetooth_output.py       ← Laptop TTS driver (pyttsx3)
│   ├── esp32_output.py           ← ESP32 SAM speech driver
│   └── audio_manager.py          ← Factory router
│
├── communication/
│   ├── websocket_server.py       ← Real-time WebSocket hub
│   ├── web_server.py             ← HTTP dashboard server
│   ├── serial_manager.py         ← USB serial driver
│   └── qr_generator.py          ← QR code generator
│
├── esp32/
│   ├── include/
│   │   ├── wifi_credentials.h            ← CREATED BY YOU (Wi-Fi secrets)
│   │   └── wifi_credentials.h.example    ← Template reference
│   └── src/
│       └── main.cpp              ← ESP32 C++ firmware
│
├── static/
│   ├── assets/                   ← QR code PNG (auto-generated)
│   ├── css/style.css             ← Dashboard styling
│   └── js/app.js                 ← Dashboard JavaScript
│
├── templates/
│   └── index.html                ← Web dashboard HTML
│
├── docs/                         ← Project documentation
│   ├── TECH_STACK.md
│   ├── PHASE_1_FOUNDATION.md
│   ├── PHASE_2_SERIAL_COMMUNICATION.md
│   ├── PHASE_3_TEXT_TO_SPEECH.md
│   ├── PHASE_4_WEBSOCKET_WIRELESS.md
│   ├── PHASE_5_ESP32_FIRMWARE.md
│   ├── PHASE_6_HMI_REDESIGN.md
│   └── PHASE_7_HARDWARE_ACTUATION.md
│
└── tests/
    └── test_tts.py               ← TTS unit tests
```

---

## ⚡ Quick Start Summary (TL;DR)

```powershell
# 1. Clone
git clone https://github.com/harshitkisoch/campus-guide-robot.git
cd campus-guide-robot

# 2. Create .env (copy from .env.example and fill your Gemini API key)
copy .env.example .env
# Edit .env with your values

# 3. Create ESP32 credentials (copy from example)
copy esp32\include\wifi_credentials.h.example esp32\include\wifi_credentials.h
# Edit wifi_credentials.h with your Wi-Fi details

# 4. Setup Python environment
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# 5. Run
python main.py
```

---

## ❓ Common Issues

| Problem | Solution |
|---------|----------|
| `No module named 'qrcode'` | Run `pip install -r requirements.txt` inside `.venv` |
| `CRITICAL CONFIG ERROR` at startup | Your `.env` file is missing or has wrong field names |
| `COM port not found` | Check Device Manager, install CP2102/CH340 USB driver |
| Phone shows "Refused to Connect" | Add Windows Firewall inbound rule for ports 8000, 8765 |
| Phone can't reach laptop on campus Wi-Fi | Use your phone's personal hotspot instead (campus Wi-Fi isolates clients) |
| Microphone shows "Error: not-allowed" | Follow the Chrome flags fix in Step 9 |
| ESP32 won't connect to WebSocket | Verify `WS_SERVER_IP` in `wifi_credentials.h` matches your laptop IP |
