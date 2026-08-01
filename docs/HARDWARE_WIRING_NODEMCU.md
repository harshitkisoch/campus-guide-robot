# 🔌 NodeMCU ESP8266 Hardware Wiring & Circuit Guide

This document provides a comprehensive, step-by-step wiring diagram for connecting your **NodeMCU ESP8266** board to the **BTS7960 High-Current Motor Driver** and the **MAX7219 4-in-1 LED Matrix Mouth Display**.

---

## 🛠️ Components Required

1. **NodeMCU ESP8266** (ESP-12E Module)
2. **BTS7960 High-Current Dual Motor Driver** (43A H-Bridge Module)
3. **MAX7219 4-in-1 Cascaded LED Matrix Module** (8x32 Red LED Display)
4. **2x DC Geared Motors** (Chassis Wheels)
5. **Battery Power Source** (7.4V - 12V Li-ion or LiPo Battery Pack for Motors)
6. **USB Power Source / Power Bank** (5V for NodeMCU & MAX7219 VCC)
7. **Jumper Wires** (Male-to-Female, Female-to-Female)

---

## 📐 Overall System Circuit Diagram

```
                              ┌─────────────────────────────┐
                              │    NodeMCU ESP8266 Board    │
                              └──────────────┬──────────────┘
                                             │
               ┌─────────────────────────────┴─────────────────────────────┐
               ▼                                                           ▼
┌──────────────────────────────┐                                ┌──────────────────────┐
│  BTS7960 Motor Driver Module │                                │ MAX7219 4-in-1 Matrix│
│ (High-Current 43A H-Bridge)  │                                │ (Animated LED Mouth) │
└──────────────┬───────────────┘                                └──────────┬───────────┘
               │                                                           │
 L_PWM / L_IN1 ──► Pin D1 (GPIO 5)                                   DIN ──► Pin D7 (GPIO 13)
 L_PWM / L_IN2 ──► Pin D2 (GPIO 4)                                   CS  ──► Pin D8 (GPIO 15)
 R_PWM / R_IN3 ──► Pin D5 (GPIO 14)                                  CLK ──► Pin D4 (GPIO 2)
 R_PWM / R_IN4 ──► Pin D6 (GPIO 12)                                  VCC ──► 5V / Vin
 R_EN & L_EN   ──► 5V / VCC (Tie HIGH)                               GND ──► Common GND
 GND           ──► Common GND
 B+ / B-       ──► 12V Motor Battery
 M+ / M-       ──► DC Motors
```

---

## 📋 Pin-by-Pin Wiring Connections Table

### 1. NodeMCU to BTS7960 Motor Driver Connection

| BTS7960 Module Pin | NodeMCU Board Pin | NodeMCU GPIO | Function / Signals |
| :--- | :--- | :--- | :--- |
| `L_PWM` (or `L_IN1`) | **Pin D1** | `GPIO 5` | Left Motor Forward Speed (PWM) |
| `L_PWM` (or `L_IN2`) | **Pin D2** | `GPIO 4` | Left Motor Reverse Speed (PWM) |
| `R_PWM` (or `R_IN3`) | **Pin D5** | `GPIO 14` | Right Motor Forward Speed (PWM) |
| `R_PWM` (or `R_IN4`) | **Pin D6** | `GPIO 12` | Right Motor Reverse Speed (PWM) |
| `R_EN` & `L_EN` | **5V / Vin** | `5V` | Tie both pins HIGH to 5V to enable driver |
| `VCC` | **3.3V / 5V** | `3.3V/5V` | Driver Logic Power |
| `GND` | **GND** | `GND` | Driver Logic Ground |

#### BTS7960 Power & Motor Output Screw Terminals:
* `B+` ──► Connect to **Battery Positive (+7.4V to +12V)**
* `B-` ──► Connect to **Battery Negative / Ground (-)**
* `M+ / M- (Left)` ──► Connect to **Left DC Motor Terminal**
* `M+ / M- (Right)` ──► Connect to **Right DC Motor Terminal**

---

### 2. NodeMCU to MAX7219 4-in-1 LED Matrix (Mouth Display)

| MAX7219 Pin | NodeMCU Board Pin | NodeMCU GPIO | Description |
| :--- | :--- | :--- | :--- |
| `DIN` | **Pin D7** | `GPIO 13` | Serial Data Input |
| `CS` | **Pin D8** | `GPIO 15` | Chip Select / Load |
| `CLK` | **Pin D4** | `GPIO 2` | Serial Clock |
| `VCC` | **5V / Vin** | `Vin (5V)` | Matrix Power (+5V) |
| `GND` | **GND** | `GND` | Matrix Power Ground |

---

## ⚡ Power Management & Common Ground Rules

> [!IMPORTANT]
> **COMMON GROUND IS MANDATORY**: You MUST connect the `GND` pin of the NodeMCU, the `GND` of the BTS7960 driver, the `GND` of the MAX7219 matrix, and the **Negative (-) terminal of your motor battery** together to a single ground rail! Without a common ground, signals will noise out.

### Recommended Battery Wiring:
* **NodeMCU & MAX7219**: Power via USB cable connected to a 5V Power Bank (or via `Vin` pin).
* **BTS7960 & Motors**: Power via a separate 2S/3S Li-ion battery pack (7.4V–11.1V) connected to `B+` and `B-` terminals.

---

## 🧪 Testing Your Wiring

1. Connect NodeMCU to your laptop via micro-USB cable.
2. Compile and upload firmware using PlatformIO:
   ```powershell
   C:\Users\Admin\.platformio\penv\Scripts\pio.exe run -e nodemcuv2 --target upload
   ```
3. Open Serial Monitor at **115200 baud**. You will see:
   ```
   [BTS7960] DC Chassis Motor drivers initialized.
   [MOUTH DISPLAY] Native ESP32 MAX7219 4-in-1 driver initialized.
   ESP32 READY
   ```
