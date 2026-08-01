# Campus Guide Robot: Technology Stack

This document details the technologies, libraries, frameworks, and tools used in the Campus Guide Robot project. It outlines the rationale for each choice and describes how each component integrates into the overall system architecture.

## 1. Python Backend (Server-Side)

### Python 3.10+
- **What it is:** A high-level, interpreted programming language known for its readability and extensive library ecosystem.
- **Why it was chosen:** Python is the industry standard for AI and robotics prototyping. While C++ or Node.js were alternatives, Python offers significantly faster development cycles, superior integration with AI APIs (like Gemini), and robust libraries for hardware communication.
- **How it's used:** Serves as the central brain of the robot, running the local HTTP and WebSocket servers, interfacing with the LLM, and orchestrating communication between the mobile dashboard and the ESP32 firmware.
- **Version:** 3.10 or higher.

### Google Gemini API (`google-genai>=0.1.1`)
- **What it is:** The official Python SDK for Google's Gemini generative AI models.
- **Why it was chosen:** Gemini was chosen over OpenAI GPT or local LLMs due to a combination of speed, cost-effectiveness (free tier availability), and the low-latency response capabilities of the `gemini-3.5-flash-lite` model, which is critical for natural conversational interactions.
- **How it's used:** Processes user speech (converted to text) and generates appropriate conversational responses and navigation commands.
- **Version:** `>=0.1.1`

### Pydantic Settings (`pydantic-settings>=2.2.1`)
- **What it is:** A library for parsing and validating configuration data and environment variables using Python type annotations.
- **Why it was chosen:** Pydantic provides robust type safety and validation at startup, ensuring that all required configurations (like API keys and network settings) are present and correctly formatted. This is far less error-prone than using raw `os.environ` or `configparser`.
- **How it's used:** Defines and loads the central configuration schema for the backend server.
- **Version:** `>=2.2.1`

### pyttsx3 (`pyttsx3>=2.90`)
- **What it is:** An offline text-to-speech (TTS) conversion library in Python.
- **Why it was chosen:** `pyttsx3` works completely offline, leveraging the built-in Windows SAPI5 engine (specifically the Microsoft Zira voice). Offline TTS is crucial for a robot operating in a campus environment where continuous internet connectivity cannot be guaranteed for cloud-based TTS services like gTTS or ElevenLabs.
- **How it's used:** Synthesizes the AI-generated text responses into audible speech on the server side (for debugging or primary audio output).
- **Version:** `>=2.90`

### PySerial (`pyserial>=3.5`)
- **What it is:** A library encapsulating access for the serial port.
- **Why it was chosen:** Serial communication was the most reliable and straightforward method for initial testing and communication with the ESP32 before transitioning to a wireless WebSocket architecture.
- **How it's used:** Used primarily in the early prototyping phases for direct USB communication with the ESP32 microcontroller.
- **Version:** `>=3.5`

### WebSockets (`websockets>=12.0`)
- **What it is:** A library for building WebSocket servers and clients in Python.
- **Why it was chosen:** WebSockets provide full-duplex, bidirectional, and real-time communication. This is ideal for robot control compared to HTTP polling (which adds latency) or MQTT (which introduces broker overhead). It is simpler and lighter than Socket.IO for this use case.
- **How it's used:** Implements the real-time messaging hub (`ws://...:8765`), handling concurrent connections from the mobile frontend and the ESP32 hardware.
- **Version:** `>=12.0`

### QR Code & Pillow (`qrcode>=7.4.2`, `pillow>=10.0.0`)
- **What it is:** Libraries for generating QR code images.
- **Why it was chosen:** Scanning a QR code provides an instantaneous, friction-free way for users to connect their mobile devices to the robot's local web dashboard, avoiding the need to manually type IP addresses.
- **How it's used:** Generates a QR code containing the URL of the mobile dashboard at startup, displaying it in the terminal or saving it as an image.
- **Version:** `qrcode>=7.4.2`, `pillow>=10.0.0`

### Zeroconf (`zeroconf>=0.132.0`)
- **What it is:** A pure Python implementation of multicast DNS (mDNS) service discovery.
- **Why it was chosen:** Allows devices to discover the robot on the local network using a friendly hostname (`campusguiderobot.local`) without relying on static IP configuration or dedicated DNS servers.
- **How it's used:** Broadcasts the HTTP and WebSocket server presence on the local network.
- **Version:** `>=0.132.0`

### Python Dotenv (`python-dotenv>=1.0.1`)
- **What it is:** Reads key-value pairs from a `.env` file and sets them as environment variables.
- **Why it was chosen:** A standard, secure way to manage sensitive credentials like API keys outside of the source code.
- **How it's used:** Loads configuration during backend startup before Pydantic validation.
- **Version:** `>=1.0.1`


## 2. ESP32 Embedded Firmware (C++)

### PlatformIO
- **What it is:** An open-source ecosystem for IoT development with a unified build system.
- **Why it was chosen:** PlatformIO is vastly superior to the standard Arduino IDE for complex projects. It offers a professional toolchain, CLI builds, excellent dependency management (via `platformio.ini`), and seamless VS Code integration.
- **How it's used:** The primary build environment and package manager for the ESP32 firmware.

### Arduino Framework on ESP32
- **What it is:** The Arduino core adapted for the Espressif ESP32 microcontroller.
- **Why it was chosen:** The Arduino framework provides rapid prototyping capabilities and access to a massive ecosystem of tested libraries. While ESP-IDF offers more granular control, the Arduino framework significantly accelerates development for this project's requirements.
- **How it's used:** The base framework for all C++ firmware code running on the ESP32.

### ESP8266SAM (v1.0.1)
- **What it is:** A port of the Software Automatic Mouth (SAM) speech synthesizer for ESP microcontrollers.
- **Why it was chosen:** SAM provides a completely offline, low-resource method to synthesize robotic speech directly on the ESP32. This avoids the complexity and network overhead of streaming I2S audio data from the Python server to the microcontroller.
- **How it's used:** Generates synthesized speech output directly on the robot hardware for localized audio feedback.
- **Version:** `v1.0.1`

### ESP8266Audio (v1.9.7)
- **What it is:** A library for playing audio files and streams on ESP8266/ESP32.
- **Why it was chosen:** Provides the necessary abstraction to output audio via the ESP32's internal 8-bit DAC or an external I2S DAC.
- **How it's used:** Routes the audio data from ESP8266SAM (or other sources) to the internal DAC on GPIO 25, which is then amplified by the HW-104 speaker module.
- **Version:** `v1.9.7`

### ArduinoWebsockets (v0.5.3)
- **What it is:** A lightweight WebSocket client and server library for Arduino.
- **Why it was chosen:** Essential for real-time, low-latency, bidirectional communication with the Python backend. WebSockets are far more responsive for motor control than HTTP REST polling and require less infrastructure than MQTT.
- **How it's used:** Connects the ESP32 to the Python WebSocket server to receive movement commands and transmit status updates.
- **Version:** `v0.5.3`

### ArduinoJson (v6.21.3)
- **What it is:** A highly efficient JSON serialization and parsing library for C++.
- **Why it was chosen:** JSON is the standard data interchange format for modern web and IoT applications. `ArduinoJson` is memory-efficient and much safer and easier to use than manual string parsing or complex binary protocols like Protocol Buffers for this scope.
- **How it's used:** Parses incoming command payloads from the WebSocket server and formats outgoing telemetry data.
- **Version:** `v6.21.3`

### L298N/TB6612FNG Motor Driver
- **What it is:** Hardware libraries/logic for controlling dual DC motors via an H-bridge.
- **Why it was chosen:** Standard, reliable method for bidirectional DC motor control.
- **How it's used:** Interfaces with the ESP32's hardware LEDC (PWM) channels to modulate speed and direction of the chassis wheels.

### SG90 Servo Motor
- **What it is:** Logic for controlling standard hobby servos.
- **Why it was chosen:** Provides simple, precise angular positioning for the robot's head.
- **How it's used:** Utilizes the ESP32's LEDC peripheral generating a 50Hz PWM signal to control the head rotation sweep.


## 3. Frontend (Mobile Dashboard)

### HTML5 + Vanilla CSS + JavaScript
- **What it is:** The foundational technologies of the web.
- **Why it was chosen:** A completely vanilla approach was chosen over frameworks like React, Vue, or Angular to minimize complexity. It allows the dashboard to be a simple Single-Page Application (SPA) served locally by the Python backend without a build step, ensuring instant loading on mobile devices.
- **How it's used:** Creates the structure, styling, and logic of the mobile control interface.

### Tailwind CSS (CDN)
- **What it is:** A utility-first CSS framework.
- **Why it was chosen:** Enables extremely rapid, mobile-first UI development directly in the HTML markup. Using it via CDN avoids npm and Node.js build dependencies, keeping the project lightweight.
- **How it's used:** Styles the entire dashboard, providing a clean, modern, and responsive layout.

### Google Material Symbols
- **What it is:** A comprehensive icon font library by Google.
- **Why it was chosen:** Provides a consistent, professional, and scalable set of icons without managing individual image assets.
- **How it's used:** Used for all UI iconography (buttons, status indicators).

### Google Fonts (Plus Jakarta Sans, JetBrains Mono)
- **What it is:** A library of free, open-source fonts.
- **Why it was chosen:** Improves readability and aesthetic appeal. 'Plus Jakarta Sans' offers a clean modern UI look, while 'JetBrains Mono' is used for code or technical readouts.
- **How it's used:** Applied globally via CSS to enhance the dashboard's typography.

### Web Speech API (SpeechRecognition)
- **What it is:** A native browser API for speech-to-text functionality.
- **Why it was chosen:** Eliminates the need to send audio streams to a paid external STT API. It leverages the browser's built-in capabilities, works offline (on supported devices after initial load), and provides `interimResults` for fast, real-time streaming feedback to the user.
- **How it's used:** Captures the user's voice commands directly from the mobile browser and converts them to text before sending them to the backend via WebSocket.

### WebSocket (Browser API)
- **What it is:** Native browser implementation of the WebSocket protocol.
- **Why it was chosen:** Standard for real-time web applications. Requires no external libraries.
- **How it's used:** Maintains a persistent connection to the Python backend to send voice text/commands and receive status updates.


## 4. Communication Architecture

- **HTTP Server (port 8000):** A lightweight Python server responsible for serving the static files (HTML, CSS, JS) that make up the mobile dashboard.
- **WebSocket Server (port 8765):** The central real-time bidirectional messaging hub. Phone browsers connect to the `/phone` path to send commands, while the ESP32 connects to the root `/` path to receive them.
- **mDNS (zeroconf):** Provides local network service discovery, allowing users to navigate to `http://campusguiderobot.local:8000` instead of a hardcoded IP address.
- **QR Code:** Automatically generated and displayed at server startup, providing an instant link to the mobile dashboard for seamless user onboarding.


## 5. Development Tools

- **VS Code:** The primary Integrated Development Environment, chosen for its speed, extensibility, and excellent support for both Python and C++ (via PlatformIO).
- **PlatformIO CLI:** Used under the hood by the VS Code extension for building, uploading, and monitoring the ESP32 firmware via serial.
- **Git:** The industry standard for version control and source code management.
- **Windows 10/11:** The primary development operating system, fundamentally relied upon for the built-in SAPI5 TTS engine used by `pyttsx3`.


## 6. Hardware Components

- **ESP32 Dev Module (38-pin):** The core microcontroller, providing Wi-Fi connectivity, ample processing power, and necessary GPIO/DAC pins.
- **HW-104 2Ω Speaker Module:** Connected to the ESP32's GPIO 25 (Internal DAC) for onboard audio output.
- **L298N / TB6612FNG Dual DC Motor Driver:** Handles the high current requirements for the chassis drive motors, controlled via logic signals from the ESP32.
- **2x DC Geared Motors:** Provide differential drive locomotion for the robot chassis.
- **SG90 Servo Motor:** Provides mechanical actuation for panning the robot's head/sensors.
- **3.7V Li-ion Battery:** The primary power source for the untethered robot.
- **Jumper wires, breadboard:** Essential for prototyping and electrical connections.
