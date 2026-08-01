# 🔑 Simple Guide: Where to Put API Keys & Quickstart Setup

Welcome! This guide explains **in simple, easy-to-understand words** where to put your API keys (Sarvam AI for Hindi Speech, Gemini AI for Brain responses) and how to run your Campus Guide Robot step by step!

---

## 📌 Step 1: Where do API Keys go? (कहाँ डालनी हैं Keys?)

All API keys are stored in a file named **`.env`** located in the main root folder of your project:
📁 `h:\campus guide robot\.env`

If the `.env` file does not exist yet, simply copy `.env.example` and rename it to `.env`:
```powershell
cp .env.example .env
```

---

## 📝 Step 2: What goes inside `.env`?

Open the `.env` file in VS Code and fill in your keys like this:

```env
# 1. Google Gemini API Keys (For Robot Brain & Personality Responses)
# Note: You can add multiple keys separated by commas for automatic round-robin rotation!
GEMINI_API_KEYS=AIzaSyA_YourKey1Here,AIzaSyB_YourKey2Here
GEMINI_MODEL=gemini-1.5-flash

# 2. Sarvam AI API Key (For Natural Hindi Speech Output)
SARVAM_API_KEY=sk_4fa27z38_s7fO7z9x6SMFaCAhkJX8uMOv

# 3. Audio Output Mode
# Options: 'sarvam' (Recommended for Hindi), 'bluetooth' (Microsoft Zira), or 'esp32'
OUTPUT_DEVICE=sarvam
```

---

## 🔑 How to get your API Keys (Step-by-Step)

### A. How to get a FREE Google Gemini API Key:
1. Open [Google AI Studio](https://aistudio.google.com/).
2. Log in with your Google account.
3. Click **"Get API Key"** ➔ **"Create API Key in new project"**.
4. Copy your key (starts with `AIzaSy...`) and paste it after `GEMINI_API_KEYS=` in `.env`.
   > 💡 **Pro Tip**: You can generate 2 or 3 keys and paste them separated by commas (`GEMINI_API_KEYS=key1,key2,key3`). If key #1 hits daily rate limit (`429`), the robot automatically switches to key #2 instantly!

---

### B. How to get a Sarvam AI Key (For Hindi Speech Output):
1. Open [Sarvam AI Dashboard](https://dashboard.sarvam.ai/).
2. Register/Log in with your phone number/email.
3. Go to **API Keys** section and click **"Create New API Key"**.
4. Copy your key (starts with `sk_...`) and paste it after `SARVAM_API_KEY=` in `.env`.

---

## 🚀 Step 3: How to Run the Robot System (Step-by-Step)

### Step 3.1: Flash NodeMCU / ESP32 Firmware (One-time Setup)
Connect your NodeMCU board to your laptop via USB and run:
```powershell
C:\Users\Admin\.platformio\penv\Scripts\pio.exe run -e nodemcuv2 --target upload
```

---

### Step 3.2: Start the Python Backend Server
Open your VS Code terminal and type:
```powershell
python main.py
```
You will see output like this in terminal:
```
================================────────────────
[INFO] Permanent QR Code image written to: static/assets/qr_code.png
[PIPELINE] Ready.
Robot is ready. Start asking questions!
```

---

### Step 3.3: Open Dashboard on Phone
1. Connect your phone to the same Wi-Fi network as your laptop.
2. Open Chrome on your phone and go to:
   **`http://172.16.14.32:8000`** *(or scan the QR code displayed in terminal)*.

---

## 📱 How to Use Your Robot:

* **🌸 AI Personality Switcher**: Tap **Cute Bestie**, **Savage Roast**, **Founder**, **Entertainer**, **Consul**, or **Viral Advisor** on your phone dashboard to switch her voice persona live!
* **🗣️ Speak or Type**: Type a question or speak into your mic. The robot will answer in a sweet Hindi voice (`Priya` speaker) while the MAX7219 LED mouth matrix animates in real-time!
* **🏎️ Touch D-Pad Driving**: Touch and hold the arrow keys on your phone dashboard to drive your BTS7960 motors and turn wheels live!
