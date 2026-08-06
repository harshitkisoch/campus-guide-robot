<div align="center">

# 🤖 Campus Guide Robot

### An AI-Powered Autonomous Campus Assistant using ESP32, Google Gemini, Python & Wireless Communication

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![ESP32](https://img.shields.io/badge/ESP32-Dev_Module-red)
![PlatformIO](https://img.shields.io/badge/PlatformIO-Embedded-orange?logo=platformio)
![Gemini](https://img.shields.io/badge/Google-Gemini_API-blue?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Under_Development-yellow)

---

### 🚀 Building an Intelligent Robot capable of Listening, Thinking and Speaking like a Human

</div>

---

### 📚 Documentation & Quickstart Guides
* 🔑 [**API Keys & Quickstart Guide** (कहाँ डालनी हैं Keys?)](file:///h:/campus%20guide%20robot/docs/API_KEYS_AND_QUICKSTART.md) — Simple step-by-step setup guide
* 🔌 [**NodeMCU Hardware Wiring Guide**](file:///h:/campus%20guide%20robot/docs/HARDWARE_WIRING_NODEMCU.md) — NodeMCU + BTS7960 Motor Driver + MAX7219 Mouth circuit diagrams
* 🎓 [**Beginner's Complete Technology Guide**](file:///h:/campus%20guide%20robot/docs/BEGINNERS_GUIDE.md) — All technologies & step-by-step learning roadmap
* 📖 [**Setup Guide for New Contributors**](file:///h:/campus%20guide%20robot/docs/SETUP_GUIDE.md) — Complete environment & dependency walkthrough
* 🏗️ [**Tech Stack Architecture**](file:///h:/campus%20guide%20robot/docs/TECH_STACK.md) — Full technical architecture breakdown

---

# 📖 Project Overview

The **Campus Guide Robot** is an AI-powered robotic assistant designed to answer questions about a university campus in natural language.

Unlike traditional robots that rely on predefined commands, this robot uses **Google Gemini AI** to understand user questions and generate intelligent responses.

The final vision is a fully interactive robot capable of:

- 🎤 Listening to users
- 🧠 Thinking using Google's Gemini AI
- 🔊 Speaking answers aloud
- 🚶 Guiding visitors around campus
- 🤖 Performing future autonomous actions

The project is being developed **incrementally**, with each subsystem completed and tested before moving to the next.

This repository contains both the **Python AI software** and the **ESP32 embedded firmware**, making it easy to clone and run on another computer.

---

# 🎯 Final Vision

```
                User

                  │

          Speaks Question

                  │

                  ▼

         Android Phone Microphone

                  │

                  ▼

              ESP32 Robot

                  │

        Sends Question via Wi-Fi

                  │

                  ▼

           Google Gemini API

                  │

          Generates Response

                  │

                  ▼

              ESP32 Speaker

                  │

                  ▼

        Robot Speaks Naturally
```

---

# ✨ Current Features

### ✅ AI Conversation

- Google Gemini Integration
- Intelligent Question Answering
- Modular AI Pipeline

---

### ✅ ESP32 Communication

- USB Serial Communication
- Wireless WebSocket Communication (In Progress)
- Modular Communication Layer

---

### ✅ Speech Output

- ESP32 Speech Synthesis
- HW-104 Amplifier Support
- 2Ω Speaker Output

---

### ✅ Project Structure

- Modular Python Architecture
- Modular Embedded Firmware
- Test Driven Development
- PlatformIO Workspace

---

# 🚧 Current Development Status

| Phase | Status |
|---------|--------|
| Project Structure | ✅ Complete |
| Python Environment | ✅ Complete |
| Gemini API | ✅ Complete |
| Serial Communication | ✅ Complete |
| ESP32 Text Reception | ✅ Complete |
| ESP32 Speech Output | ✅ Complete |
| GitHub Repository | ✅ Complete |
| Wireless WebSocket | 🚧 In Progress |
| Phone Microphone | ⏳ Planned |
| Campus RAG Database | ⏳ Planned |
| Autonomous Navigation | ⏳ Planned |

---

# 🏗️ System Architecture

```
                        USER

                          │

                  Types / Speaks

                          │

                          ▼

                Python Application

                          │

               Gemini API Processing

                          │

          Generates Intelligent Reply

                          │

              WebSocket / Serial

                          │

                          ▼

                      ESP32

                          │

                Speech Synthesis

                          │

                          ▼

                    HW-104 Amplifier

                          │

                          ▼

                    2Ω Speaker
```

---

# 📂 Repository Structure

```
Campus Guide Robot/

│

├── audio/
│      Audio playback and synthesis utilities

│

├── brain/
│      AI logic and Gemini integration

│

├── communication/
│      Serial communication
│      WebSocket communication

│

├── config/
│      Configuration management

│

├── core/
│      Main AI pipeline

│

├── esp32/
│      Complete ESP32 firmware

│      ├── include/
│      └── src/

│

├── tests/
│      Unit tests
│      Integration tests
│      Communication tests

│

├── demo.py
│      Demo application

│

├── main.py
│      Main AI application

│

├── platformio.ini
│      ESP32 PlatformIO configuration

│

├── requirements.txt
│      Python dependencies

│

└── README.md
```

---

# 💻 Technologies Used

## Programming Languages

- Python
- C++
- JSON

---

## AI

- Google Gemini API
- Prompt Engineering

---

## Embedded

- ESP32 Dev Module
- Arduino Framework
- PlatformIO

---

## Communication

- USB Serial
- WebSocket
- Wi-Fi

---

## Audio

- ESP8266SAM
- Internal ESP32 DAC
- HW-104 Amplifier

---

## Development Tools

- VS Code
- PlatformIO
- Git
- GitHub
- Python Virtual Environment

---
# 🛠️ Hardware Requirements

The following hardware is required to run the complete Campus Guide Robot.

| Hardware | Quantity | Purpose |
|-----------|----------|---------|
| ESP32 Dev Module | 1 | Main Robot Controller |
| HW-104 / PAM8403 Amplifier | 1 | Speaker Amplification |
| 2Ω Speaker | 1 | Voice Output |
| USB Cable | 1 | Programming ESP32 |
| Android Phone | 1 | Future Voice Input |
| Laptop / PC | 1 | AI Processing |
| Wi-Fi Network | 1 | ESP32 Communication |

---

# 💻 Software Requirements

Install the following software before cloning the repository.

| Software | Version |
|-----------|----------|
| Windows 10 / 11 | Recommended |
| Python | 3.10 or above |
| VS Code | Latest |
| Git | Latest |
| PlatformIO | Latest |
| Google Chrome | Latest |

---

# 📥 Required Downloads

## 1. Python

Download Python:

https://www.python.org/downloads/

During installation make sure you check:

✅ Add Python to PATH

Verify installation:

```bash
python --version
```

Expected Output

```text
Python 3.10.x
```

---

## 2. Git

Download Git:

https://git-scm.com/downloads

Verify installation

```bash
git --version
```

Expected

```text
git version 2.xx.x.windows.x
```

---

## 3. Visual Studio Code

Download

https://code.visualstudio.com/

Recommended Extensions

- Python
- Pylance
- PlatformIO IDE
- C/C++
- Error Lens
- GitLens
- Better Comments
- Markdown All in One

---

## 4. CP210x Driver

Required for ESP32 USB Communication.

Download

https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

After installation reconnect the ESP32.

Verify COM Port

Open

Device Manager

↓

Ports (COM & LPT)

You should see

```
Silicon Labs CP210x USB to UART Bridge (COMx)
```

---

## 5. PlatformIO

Open VS Code

Extensions

Search

```
PlatformIO IDE
```

Install

Restart VS Code.

---

# 📂 Clone Repository

Clone the project

```bash
git clone https://github.com/YOUR_USERNAME/campus-guide-robot.git
```

Move into project

```bash
cd campus-guide-robot
```

---

# 🐍 Create Python Virtual Environment

Create environment

```bash
python -m venv .venv
```

Activate

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
.venv\Scripts\activate
```

Expected

```
(.venv)
```

appears before your terminal path.

---

# 📦 Install Python Dependencies

Install packages

```bash
pip install -r requirements.txt
```

Verify

```bash
pip list
```

Some important packages should appear

```
google-genai

pyserial

websockets

python-dotenv

pydantic

requests

colorama
```

---

# 🔑 Configure Environment Variables

Create a file

```
.env
```

Copy contents from

```
.env.example
```

Example

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

SERIAL_PORT=COM9

SERIAL_BAUD_RATE=115200

HOST=0.0.0.0

PORT=8000

WS_HOST=0.0.0.0

WS_PORT=8765
```

⚠ Never upload your real `.env` file to GitHub.

---

# 📶 Configure ESP32 Wi-Fi

Inside

```
esp32/include/
```

Create

```
wifi_credentials.h
```

Copy contents from

```
wifi_credentials.h.example
```

Example

```cpp
#ifndef WIFI_CREDENTIALS_H
#define WIFI_CREDENTIALS_H

#define WIFI_SSID "YOUR_WIFI"

#define WIFI_PASSWORD "YOUR_PASSWORD"

#define WS_SERVER_IP "YOUR_LAPTOP_IP"

#define WS_SERVER_PORT 8765

#endif
```

---

# 🌐 Find Your Laptop IP Address

Run

```bash
python -c "import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0])"
```

Example Output

```
192.168.1.105
```

Update

```cpp
#define WS_SERVER_IP "192.168.1.105"
```

---

# 🔌 Upload ESP32 Firmware

Open

```
esp32/
```

using PlatformIO.

Connect ESP32.

Upload

```bash
PlatformIO: Upload
```

or

```bash
pio run --target upload
```

Wait until

```
SUCCESS
```

appears.

---

# ✅ Verify ESP32

Open Serial Monitor

Expected

```
Connecting WiFi...

Connected!

IP Address:

192.168.x.x

ESP32 READY
```

---

# 🧪 Verify Python Setup

Run

```bash
python tests/test_config.py
```

Expected

```
SUCCESS
```

---

Run

```bash
python tests/test_serial.py
```

Expected

```
ESP32 READY

Received:
Hello ESP32
```

---

Run

```bash
python demo.py
```

Expected

```
Ask Gemini:
```

Type

```
Hello
```

Gemini should generate a response.

---

# ▶ Running the Main Project

Run

```bash
python main.py
```

Current Flow

```
Keyboard

↓

Gemini API

↓

Python

↓

ESP32

↓

Speaker
```

The robot should now answer your typed questions through the connected speaker.

---

# ✅ Installation Checklist

- [ ] Python Installed
- [ ] Git Installed
- [ ] VS Code Installed
- [ ] PlatformIO Installed
- [ ] CP210x Driver Installed
- [ ] Repository Cloned
- [ ] Virtual Environment Created
- [ ] Dependencies Installed
- [ ] Gemini API Added
- [ ] Wi-Fi Credentials Configured
- [ ] ESP32 Firmware Uploaded
- [ ] Tests Passed
- [ ] Demo Running Successfully
# 🏛️ Software Architecture

The Campus Guide Robot follows a **modular layered architecture**.

Each module has a single responsibility, making the system easier to debug, test, and extend.

```
                         USER
                           │
            ┌──────────────┴──────────────┐
            │                             │
      Keyboard Input              (Future) Phone Mic
            │                             │
            └──────────────┬──────────────┘
                           │
                           ▼
                    Python Application
                           │
                   Input Processing Layer
                           │
                           ▼
                    Gemini AI Engine
                           │
                   Response Processing
                           │
                           ▼
                 Communication Layer
                  (Serial / WebSocket)
                           │
                           ▼
                        ESP32
                           │
                 Speech Synthesis Layer
                           │
                           ▼
                    Audio Amplifier
                           │
                           ▼
                        Speaker
```

---

# 📂 Folder Structure Explained

```
Campus Guide Robot
│
├── audio/
├── brain/
├── communication/
├── config/
├── core/
├── esp32/
├── tests/
├── demo.py
├── main.py
└── requirements.txt
```

---

# 📁 audio/

Responsible for every audio-related task.

Current responsibilities:

- Speaker playback
- Audio utilities

Future responsibilities:

- Text-to-Speech
- Audio buffering
- Streaming audio

---

# 📁 brain/

This is the **AI Brain** of the robot.

Responsibilities

- Gemini API
- Prompt generation
- Response generation
- Future RAG

Current Flow

```
Question

↓

Gemini API

↓

Response
```

Future

```
Question

↓

Campus Documents

↓

Gemini

↓

Better Response
```

---

# 📁 communication/

This module handles communication between the laptop and the ESP32.

Currently supports

- USB Serial
- WebSocket

Future

- Bluetooth
- MQTT (optional)
- OTA Updates

Architecture

```
Python

↓

Communication Layer

↓

ESP32
```

Keeping communication separate means the AI never needs to know **how** the ESP32 is connected.

---

# 📁 config/

Contains all configuration files.

Examples

```
API Keys

Serial Port

Wi-Fi

Server Ports

Model Names
```

Nothing inside the application should hardcode these values.

---

# 📁 core/

This is where the complete AI pipeline lives.

Responsibilities

- Receive user input
- Send prompt to Gemini
- Receive AI response
- Clean response
- Send response to ESP32

Think of this folder as the robot's "brainstem" that coordinates all modules.

---

# 📁 esp32/

Contains all firmware running on the robot.

Responsibilities

- Wi-Fi Connection
- WebSocket Client
- Serial Communication
- Speaker Control
- Speech Synthesis

Current Firmware Flow

```
Receive Text

↓

Speak Text

↓

Wait for Next Message
```

Future

```
Receive Command

↓

Move Robot

↓

Speak

↓

Read Sensors

↓

Send Status
```

---

# 📁 tests/

Every major subsystem has its own test.

Examples

```
test_config.py

test_serial.py

test_gemini.py

test_audio.py

test_websocket.py
```

Testing every subsystem individually makes debugging much easier.

---

# 🧠 AI Pipeline

Current

```
Keyboard

↓

main.py

↓

Pipeline

↓

Gemini Client

↓

Gemini API

↓

Response

↓

Communication

↓

ESP32

↓

Speaker
```

---

# 📡 Communication Layer

One of the biggest design decisions in this project is separating **AI** from **hardware communication**.

```
            AI

             │

      Communication

             │

          Hardware
```

This means the AI code does not need to know whether the ESP32 is connected using

- USB
- Wi-Fi
- Bluetooth

Only the communication module changes.

---

# 🔊 Audio Pipeline

Current

```
Gemini Response

↓

Python

↓

ESP32

↓

Speech Synthesis

↓

Internal DAC

↓

HW-104 Amplifier

↓

2Ω Speaker
```

Future

```
Gemini Response

↓

Streaming Audio

↓

ESP32

↓

Amplifier

↓

Speaker
```

---

# 🧠 Why Use a Modular Architecture?

Instead of writing one giant file, each subsystem has one responsibility.

Benefits

✅ Easier debugging

✅ Easier testing

✅ Easier upgrades

✅ Better collaboration

✅ Cleaner codebase

---

# 🔄 Complete Data Flow

Current Working Flow

```
User

↓

Keyboard

↓

Python

↓

Gemini

↓

Gemini Response

↓

Communication Layer

↓

ESP32

↓

Speech Synthesis

↓

Speaker
```

Future Flow

```
User

↓

Phone Microphone

↓

Speech-to-Text

↓

Gemini AI

↓

Campus Knowledge (RAG)

↓

Decision Layer

↓

ESP32

↓

Motors

↓

Speaker

↓

Robot Action
```

---

# 🔌 ESP32 Responsibilities

The ESP32 is responsible for **hardware control**, not AI reasoning.

Current Responsibilities

- Receive messages
- Manage Wi-Fi
- Maintain WebSocket connection
- Synthesize speech
- Play audio

Future Responsibilities

- Servo control
- Motor control
- LEDs
- Gesture control
- Battery monitoring
- Sensor readings
- Obstacle detection

---

# 🧩 Python Responsibilities

Python acts as the robot's intelligence layer.

Current Responsibilities

- User interaction
- Gemini API
- Prompt management
- Communication
- Testing

Future Responsibilities

- RAG
- Memory
- Navigation logic
- Conversation history
- Logging
- Analytics

---

# 🚀 Future Expansion

The project has been designed so that new capabilities can be added **without rewriting the existing codebase**.

Planned features include:

- 🎤 Phone microphone input
- 📚 Campus RAG database
- 👤 Face recognition (optional)
- 😊 Animated robot face
- 🦾 Gesture-controlled arms
- 🚶 Autonomous navigation
- 🛰️ OTA firmware updates
- 📊 Robot telemetry dashboard
# 🧪 Testing

Before running the complete project, verify each subsystem individually.

---

## 1. Configuration Test

```bash
python tests/test_config.py
```

Expected Output

```
Configuration Loaded Successfully
```

---

## 2. Gemini API Test

```bash
python tests/test_gemini.py
```

Expected Output

```
Hello!
I'm Gemini...
```

---

## 3. Serial Communication Test

```bash
python tests/test_serial.py
```

Expected Output

```
ESP32 READY

Received:
Hello ESP32
```

---

## 4. WebSocket Communication Test

```bash
python tests/test_esp32_ws.py
```

Expected Output

```
ESP32 Connected

Waiting for Messages...
```

---

## 5. Speaker Test

Run

```bash
python demo.py
```

Type

```
Hello
```

Expected

```
Gemini generates response

↓

ESP32 receives response

↓

Speaker speaks response
```

---

# 🐞 Troubleshooting

## Git Not Recognized

Problem

```
git is not recognized...
```

Solution

- Install Git
- Restart VS Code
- Verify

```bash
git --version
```

---

## Python Not Recognized

Install Python from

https://python.org

Enable

```
Add Python to PATH
```

Verify

```bash
python --version
```

---

## COM Port Not Found

Check

Device Manager

↓

Ports

↓

CP210x USB UART

Update

```
SERIAL_PORT=COMx
```

inside

```
.env
```

---

## Gemini API Error

Check

```
GEMINI_API_KEY
```

inside

```
.env
```

Ensure the API key is valid and active.

---

## ESP32 Does Not Connect to Wi-Fi

Verify

```
wifi_credentials.h
```

Check

```
SSID

Password

Laptop IP
```

Ensure both the laptop and ESP32 are connected to the same **2.4 GHz Wi-Fi** network.

---

## No Audio Output

Verify

- HW-104 amplifier wiring
- Speaker polarity
- GPIO25 DAC output
- Amplifier power supply

---

## WebSocket Timeout

Check

- Laptop firewall
- Laptop IP address
- ESP32 IP address
- Same Wi-Fi network
- WebSocket port (8765)

---

# 📋 Development Workflow

This project follows an incremental development strategy.

Each phase is completed and tested before moving to the next.

```
Design

↓

Implement

↓

Test

↓

Debug

↓

Git Commit

↓

GitHub Push

↓

Next Phase
```

This approach ensures that every milestone remains stable and reproducible.

---

# 🗺️ Roadmap

## ✅ Phase 1

- Project Setup
- Python Environment
- Gemini API
- Configuration

Status

✔ Complete

---

## ✅ Phase 2

- ESP32 Firmware
- Serial Communication
- Echo Testing

Status

✔ Complete

---

## ✅ Phase 3

- Speaker Output
- Speech Synthesis
- Audio Pipeline

Status

✔ Complete

---

## ✅ Phase 4

- GitHub Repository
- Documentation
- WebSocket Foundation

Status

✔ Complete

---

## 🚧 Phase 5

- Stable Wireless Communication
- Keyboard → Gemini → ESP32
- Speaker Response

Status

In Progress

---

## 📅 Phase 6

Phone Microphone Integration

Goal

```
Phone

↓

Speech

↓

Gemini

↓

ESP32

↓

Speaker
```

---

## 📅 Phase 7

Campus Knowledge Base

- University FAQs
- Faculty Information
- Department Information
- Campus Map
- Events

(RAG Integration)

---

## 📅 Phase 8

Robot Face

- OLED Display
- Eye Animation
- Speaking Animation
- Status Indicators

---

## 📅 Phase 9

Robot Body

- Servo Head
- Arm Gestures
- LED Expressions

---

## 📅 Phase 10

Navigation

- Motors
- Obstacle Detection
- Path Planning
- Autonomous Movement

---

## 🎯 Final Vision

```
Student

↓

Phone Microphone

↓

Speech Recognition

↓

Gemini AI

↓

Campus Knowledge

↓

Decision Layer

↓

ESP32

↓

Motors

↓

Speaker

↓

Campus Guide Robot
```

---

# 🤝 Contributing

Contributions are welcome.

If you would like to improve this project:

1. Fork the repository

2. Create a new branch

```
git checkout -b feature/my-feature
```

3. Commit changes

```
git commit -m "Added new feature"
```

4. Push

```
git push origin feature/my-feature
```

5. Open a Pull Request.

Please ensure all tests pass before submitting changes.

---

# 📜 License

This project is licensed under the MIT License.

You are free to:

- Use
- Modify
- Distribute
- Learn from the project

while retaining the original license.

---

# 🙏 Acknowledgements

Special thanks to:

- Google Gemini API
- ESP32 Community
- PlatformIO Team
- Arduino Community
- Open Source Contributors

---

# 👨‍💻 Author

**Harshit Maheshwari**

B.Tech Computer Science (AI & Data Science)

AI • Robotics • Embedded Systems • Automation

GitHub:

https://github.com/harshitkisoch

---

# ⭐ Support

If you found this project useful:

⭐ Star this repository

🍴 Fork the repository

🐛 Report issues

💡 Suggest improvements

Every contribution helps make this project better.

---

# 📬 Contact

For questions, ideas, or collaborations, please open an Issue or Discussion on this repository.

---

<div align="center">

## ⭐ If you like this project, consider giving it a Star!

### Thank you for visiting the Campus Guide Robot repository 🤖

**Happy Building! 🚀**

</div>
