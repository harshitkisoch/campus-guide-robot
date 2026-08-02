# 🚀 Campus Guide Robot — Complete Setup & Developer Guide

Welcome to the **Campus Guide Robot** project! This guide is written in simple, clear, step-by-step instructions so that anyone cloning this repository can easily set up, run, test, and build upon the robot codebase.

---

## 🎯 What is this Robot? (Quick Overview)

The **Campus Guide Robot** is an intelligent AI assistant built with:
* 🧠 **Google Gemini AI**: Answers any question with 7 selectable AI personalities (Cute Bestie, Savage Roast, Founder, Entertainer, Consul, Viral Advisor, Formal Guide).
* 🗣️ **Sarvam AI Hindi Speech Engine**: Speaks natural Hindi audio using the female `Priya` voice.
* 📱 **Mobile HMI Companion App**: A web app for your phone with touch D-Pad driving, haptic vibration, and real-time response bubbles.
* 🤖 **NodeMCU ESP8266 & BTS7960 Motor Driver**: Drives chassis wheels and animates an **8x32 MAX7219 LED Matrix Mouth** in real-time while talking!

---

## 📋 Step 1: Prerequisites & Downloads

Before starting, install these tools on your computer:

| Software | Purpose | Download Link |
| :--- | :--- | :--- |
| **Python 3.10+** | Runs the AI server & voice pipeline | [python.org/downloads](https://www.python.org/downloads/) |
| **Git** | Clones & updates the code | [git-scm.com](https://git-scm.com/downloads) |
| **VS Code** | Code editor | [code.visualstudio.com](https://code.visualstudio.com/) |
| **PlatformIO Extension** | Builds & flashes firmware to NodeMCU/ESP32 | Install inside VS Code Extensions tab (`Ctrl+Shift+X`) |

> [!IMPORTANT]
> When installing Python, **CHECK THE BOX that says "Add Python to PATH"**.

---

## 📥 Step 2: Clone the Repository

Open your terminal (PowerShell or Command Prompt) and run:

```powershell
git clone https://github.com/harshitkisoch/campus-guide-robot.git
cd campus-guide-robot
```

---

## 📦 Step 3: Install Python Dependencies

Install all required Python libraries with a single command:

```powershell
pip install -r requirements.txt
```

---

## 🔑 Step 4: Configure API Keys (`.env` File)

The project uses a private environment file named `.env` to store your secret API keys.

### 4.1 Create the `.env` file
Copy the `.env.example` template to create your `.env` file:
```powershell
cp .env.example .env
```

### 4.2 Open `.env` and fill in your keys
Open `.env` in VS Code and update these fields:

```env
# 1. Google Gemini API Keys (For Robot Intelligence)
# Get FREE keys from: https://aistudio.google.com/
GEMINI_API_KEYS=YOUR_GEMINI_KEY_HERE
GEMINI_MODEL=gemini-1.5-flash

# 2. Sarvam AI API Key (For Hindi Speech Output - Priya Female Voice)
# Get FREE key from: https://dashboard.sarvam.ai/
SARVAM_API_KEY=YOUR_SARVAM_API_KEY_HERE

# 3. Audio Output Mode ('sarvam' for Hindi, 'bluetooth' for Zira, or 'esp32')
OUTPUT_DEVICE=sarvam

# 4. Speech Rate & Volume
TTS_RATE=160
TTS_VOLUME=1.0

# 5. WebSocket Router Settings
WS_HOST=0.0.0.0
WS_PORT=8765
```

> 💡 **Multi-Key Rotation Tip**: You can add 2 or 3 Gemini keys separated by commas (`GEMINI_API_KEYS=key1,key2,key3`). If key #1 hits daily rate limits, the system automatically rotates to key #2 without stopping!

---

## 📶 Step 5: Configure Hardware Wi-Fi (`wifi_credentials.h`)

Navigate to `esp32/include/` and create `wifi_credentials.h`:

```cpp
#ifndef WIFI_CREDENTIALS_H
#define WIFI_CREDENTIALS_H

// Your Wi-Fi network credentials
#define WIFI_SSID       "YOUR_WIFI_NAME"
#define WIFI_PASSWORD   "YOUR_WIFI_PASSWORD"

// Your laptop's local IP address (find using 'ipconfig' in terminal)
#define WS_SERVER_IP    "172.16.14.32"
#define WS_SERVER_PORT  8765

#endif
```

---

## 🔌 Step 6: Hardware Wiring & Firmware Upload

### 6.1 Wiring Quick Summary (NodeMCU ESP8266)
* **BTS7960 Motor Driver**: `L_PWM` ➔ `D1`, `L_PWM2` ➔ `D2`, `R_PWM` ➔ `D5`, `R_PWM2` ➔ `D6`, `R_EN & L_EN` ➔ `5V`.
* **MAX7219 Mouth Display**: `DIN` ➔ `D7`, `CS` ➔ `D8`, `CLK` ➔ `D4`, `VCC` ➔ `5V`, `GND` ➔ `Common GND`.
> 📖 Detailed circuit diagrams are available in [`docs/HARDWARE_WIRING_NODEMCU.md`](file:///h:/campus%20guide%20robot/docs/HARDWARE_WIRING_NODEMCU.md).

### 6.2 Upload Firmware to NodeMCU
Connect your NodeMCU board via USB cable and run:
```powershell
C:\Users\Admin\.platformio\penv\Scripts\pio.exe run -e nodemcuv2 --target upload
```

---

## 🚀 Step 7: Start the Robot System

Start the Python backend server:
```powershell
python main.py
```

Terminal output will show:
```
================================────────────────--
[INFO] Permanent QR Code image written to: static/assets/qr_code.png
[PIPELINE] Ready.
Robot is ready. Start asking questions!
```

---

## 📱 Step 8: Connect Phone & Control Live

1. Make sure your phone is connected to the same Wi-Fi network.
2. Open Chrome on your phone and go to: `http://<YOUR_LAPTOP_IP>:8000` (or scan the QR code).
3. **Features to Try**:
   * 🌸 **7 AI Personalities**: Tap **Cute Bestie**, **Savage Roast**, **Founder**, **Entertainer**, **Consul**, **Viral Advisor**, or **Formal Guide**.
   * 🌐 **3 Response Languages**: Tap **Hindi**, **English**, or **Hinglish** below History!
   * 🏎️ **Touch D-Pad**: Press and hold arrow keys to drive wheels live!

---

## ⏩ Step 9: How to Work Forward (Future Roadmap)

If you are cloning this repository to build new features, here are recommended next steps:

1. **🗺️ Autonomous Campus Navigation Guide**:
   * Extend `config/campus_map.py` to map landmark routes (*Library*, *Auditorium*, *Cafeteria*, *Block A*).
   * Bind landmark buttons to execute drive sequences (`up` for 2s ➔ `right` for 1s ➔ `stop`) while speaking turn-by-turn Hindi directions.

2. **📸 Camera Face Tracking**:
   * Integrate OpenCV (`opencv-python`) in `main.py` using a webcam to detect human faces and auto-orient the robot toward visitors.

3. **🔋 Battery & Sensor Telemetry**:
   * Connect an analog battery voltage divider to NodeMCU pin `A0` to send live battery % telemetry over WebSockets to the mobile dashboard.
