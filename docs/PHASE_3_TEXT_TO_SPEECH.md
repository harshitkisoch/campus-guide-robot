# Phase 3 – Dual-Channel Text-to-Speech Audio System

## 1. Objective
To endow the robot with a voice, Phase 3 focused on developing a flexible, dual-channel Text-to-Speech (TTS) system. This architecture allows the robot's responses to be spoken aloud either through the host machine's audio stack or natively on the ESP32 hardware.

## 2. What was Built

### 2.1 Abstract Interface (`audio/base_output.py`)
Defined an Abstract Base Class (ABC) `BaseAudioOutput` enforcing a strict `speak(text: str)` contract. This guarantees interchangeable audio drivers.

### 2.2 Bluetooth / Local Output (`audio/bluetooth_output.py`)
Implemented `BluetoothAudioOutput` utilizing the `pyttsx3` library.
- **Engine:** Interacts with the Windows SAPI5 engine.
- **Voice:** Specifically configured to use the 'Microsoft Zira' voice for a clear, robotic yet pleasant tone.
- **Configuration:** Dynamically sets speech rate and volume based on parameters from `settings.py`.

### 2.3 Hardware Output (`audio/esp32_output.py`)
Implemented `ESP32AudioOutput` to offload speech synthesis to the microcontroller.
- **Sanitization:** Cleans AI-generated text by stripping non-ASCII characters and truncating to a 120-character maximum (a limitation of the hardware SAM engine).
- **Transport:** Packages the sanitized string into a JSON command and transmits it over WebSockets to the ESP32.

### 2.4 Audio Routing (`audio/audio_manager.py`)
The `AudioManager` acts as a factory and router. It reads the `OUTPUT_DEVICE` config (e.g., 'bluetooth' or 'esp32') and instantiates the correct concrete class, abstracting the complexity from the main pipeline.

### 2.5 ESP32 Firmware Implementation
- Added a `speakText()` function.
- Integrated the `ESP8266SAM` library for retro, formant-based speech synthesis directly on the MCU.
- Routed the synthesized audio data through the ESP32's internal I2S DAC (Digital-to-Analog Converter) on GPIO 25.
- Output drives an HW-104 audio amplifier module connected to a 2Ω speaker.

## 3. Strategy Pattern and Architecture
The audio system relies heavily on the **Strategy Pattern**. By relying on the `BaseAudioOutput` interface, the core pipeline does not need to know *how* audio is played. Adding a new output method (e.g., a networked IP speaker) simply requires implementing the `speak()` method in a new file, adhering strictly to the Open/Closed principle.

```mermaid
flowchart TD
    Pipeline[core.pipeline] --> Manager[audio_manager.py]
    Manager -->|Device='bluetooth'| BT[bluetooth_output.py]
    Manager -->|Device='esp32'| HW[esp32_output.py]
    BT --> HostAudio[Host Audio Stack (SAPI5)]
    HW --> Socket[WebSocket Tx] --> ESP[ESP32 SAM Engine]
```

```text
                    +----------------+
                    |    Pipeline    |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | AudioManager   |
                    +-------+--------+
                           / \
            'bluetooth'   /   \   'esp32'
                         v     v
        +----------------+     +----------------+
        |BluetoothOutput |     |  ESP32Output   |
        +----------------+     +----------------+
```

## 4. Challenges Addressed
- **`pyttsx3` Lifecycle on Windows:** The COM objects used by SAPI5 often freeze if instantiated once globally. The wrapper was designed to carefully manage the initialization and destruction of the engine engine per `speak()` call, or run it within a dedicated daemon thread.
- **SAM Constraints:** The ESP8266SAM engine crashes on special Unicode characters (e.g., emojis, em-dashes). A robust regex-based sanitization step was mandatory.
- **DAC Quality:** The internal 8-bit DAC of the ESP32 is noisy. Careful software volume leveling and hardware filtering (capacitors) were necessary to achieve understandable speech.

## 5. Files Created / Modified

| Filename | Purpose |
| :--- | :--- |
| `audio/base_output.py` | ABC defining the audio interface. |
| `audio/bluetooth_output.py` | Local TTS implementation using pyttsx3. |
| `audio/esp32_output.py` | Remote TTS implementation packing text for hardware. |
| `audio/audio_manager.py` | Factory class to instantiate the correct driver. |
| `esp32/src/main.cpp` | Added ESP8266SAM integration and DAC I2S setup. |
