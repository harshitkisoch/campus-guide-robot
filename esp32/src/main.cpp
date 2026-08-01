/**
 * Campus Guide Robot - Phase 5 Hybrid Firmware
 * Supports BOTH:
 * 1. Wireless Acks & speaking status events (for Laptop Bluetooth mode)
 * 2. Wireless Text-to-Speech synthesis using SAM on GPIO 25 (for HW-104 fallback mode)
 * Prepares structure for future motor and gesture controls.
 */

#include <Arduino.h>

#ifdef ESP8266
  #include <ESP8266WiFi.h>
  // ESP8266 NodeMCU Pin Architecture (D1-D8 mappings)
  #define MOTOR_LEFT_IN1      5  // D1
  #define MOTOR_LEFT_IN2      4  // D2
  #define MOTOR_RIGHT_IN3     14 // D5
  #define MOTOR_RIGHT_IN4     12 // D6
  #define PWM_LEFT_EN         5
  #define PWM_RIGHT_EN        14
  #define SERVO_ROTATION_PIN  0  // D3
  #define LED_MATRIX_DIN      13 // D7
  #define LED_MATRIX_CLK      2  // D4
  #define LED_MATRIX_CS       15 // D8
  #define LED_MATRIX_COUNT    4
#else
  #include <WiFi.h>
  // ESP32 Dev Module Pin Architecture
  #define MOTOR_LEFT_IN1      16
  #define MOTOR_LEFT_IN2      17
  #define MOTOR_RIGHT_IN3     18
  #define MOTOR_RIGHT_IN4     19
  #define PWM_LEFT_EN         14
  #define PWM_RIGHT_EN        27
  #define SERVO_ROTATION_PIN  13
  #define LED_MATRIX_DIN      23
  #define LED_MATRIX_CLK      18
  #define LED_MATRIX_CS       5
  #define LED_MATRIX_COUNT    4
  
  // LEDC channels (ESP32 PWM managers)
  #define LEDC_LEFT_CHANNEL   1
  #define LEDC_RIGHT_CHANNEL  2
  #define LEDC_SERVO_CHANNEL  3
#endif

#include <ESP8266SAM.h>
#include <AudioOutputI2S.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>
#include "wifi_credentials.h"

using namespace websockets;

// --- Selection 1: Row 2, Frame 4 (Neutral/Resting Mouth) ---
byte frameRow2Col4[8][4] = {
  {0x00, 0x00, 0x00, 0x00},
  {0x00, 0x00, 0x00, 0x00},
  {0x0C, 0x3C, 0x3C, 0x30}, // Curved lip line
  {0x06, 0x00, 0x00, 0x60},
  {0x03, 0xFF, 0xFF, 0xC0}, // Main mouth closure
  {0x00, 0x7E, 0x7E, 0x00},
  {0x00, 0x00, 0x00, 0x00},
  {0x00, 0x00, 0x00, 0x00}
};

// --- Selection 2: Row 4, Frame 4 (Small Open / Transition) ---
byte frameRow4Col4[8][4] = {
  {0x00, 0x00, 0x00, 0x00},
  {0x00, 0x38, 0x1C, 0x00},
  {0x06, 0x44, 0x22, 0x60},
  {0x03, 0x80, 0x01, 0xC0}, // Slight opening gap
  {0x03, 0x80, 0x01, 0xC0},
  {0x01, 0xC0, 0x03, 0x80},
  {0x00, 0x7F, 0xFE, 0x00},
  {0x00, 0x00, 0x00, 0x00}
};

// --- Selection 3: Row 3, Frame 2 (Medium Open Talk) ---
byte frameRow3Col2[8][4] = {
  {0x00, 0x00, 0x00, 0x00},
  {0x00, 0x7C, 0x3E, 0x00},
  {0x03, 0xC0, 0x03, 0xC0},
  {0x07, 0x00, 0x00, 0xE0}, // Clear inner cavity
  {0x07, 0x00, 0x00, 0xE0},
  {0x03, 0xE0, 0x07, 0xC0},
  {0x01, 0xFF, 0xFF, 0x80},
  {0x00, 0x3E, 0x7C, 0x00}
};

// --- Selection 4: Row 3, Frame 3 (Wide Open / Accent Syllables) ---
byte frameRow3Col3[8][4] = {
  {0x00, 0x00, 0x00, 0x00},
  {0x00, 0xFE, 0x7F, 0x00},
  {0x03, 0x80, 0x01, 0xC0},
  {0x07, 0x00, 0x00, 0xE0}, // Wide open tall mouth
  {0x07, 0x00, 0x00, 0xE0},
  {0x03, 0x80, 0x01, 0xC0},
  {0x01, 0xC0, 0x03, 0x80},
  {0x00, 0x7F, 0xFE, 0x00}
};

// Real-time LED Mouth Animation state
bool isSpeakingMouth = false;
unsigned long lastMouthFrameTime = 0;
int currentMouthInterval = 100;

// LEDC channels (ESP32 PWM managers)
#define LEDC_LEFT_CHANNEL   1
#define LEDC_RIGHT_CHANNEL  2
#define LEDC_SERVO_CHANNEL  3

// Current robot state parameters
int currentSpeed = 50;
int currentHeadAngle = 90;
bool isServoTracking = false;

// Global Hardware Output pointer (for direct HW-104 playback)
AudioOutputI2S *audioOut = nullptr;

// Global WebSocket Client object
WebsocketsClient wsClient;

// Timing variables for non-blocking server reconnection attempts
unsigned long lastWsConnectAttempt = 0;
const unsigned long wsConnectInterval = 5000; // Retry connection every 5 seconds

// Timing variables for connection heartbeat pinging
unsigned long lastHeartbeat = 0;
const unsigned long heartbeatInterval = 10000; // Heartbeat packet every 10 seconds

// Forward declarations of helper functions
void connectToWiFi();
void connectToWebSocket();
void onMessageCallback(WebsocketsMessage message);
void onEventsCallback(WebsocketsEvent event, String data);
void speakText(const String &text);
void initChassisMotors();
void initHeadServo();
void initLedMatrix();
void updateMouthAnimation();
void drawMouthFrame(byte frame[8][4]);
void driveRobot(const String &cmd, int speedPercent);
void setHeadAngle(int degrees);
void toggleServoTracking(bool enabled);

void setup() {
  // 1. Initialize Serial debugging at 115200 baud
  Serial.begin(115200);
  delay(500);

  // 2. Initialize Internal 8-bit DAC Output (automatically routes to GPIO 25)
  audioOut = new AudioOutputI2S(0, AudioOutputI2S::INTERNAL_DAC);
  audioOut->begin();

  // 3. Connect to the local Wi-Fi router
  connectToWiFi();

  // 4. Configure WebSocket callbacks for message reception and status changes
  wsClient.onMessage(onMessageCallback);
  wsClient.onEvent(onEventsCallback);

  // 5. Attempt initial connection to Python WebSocket server
  connectToWebSocket();

  // 6. Initialize DC Motor outputs, Head Servo & LED Mouth Matrix
  initChassisMotors();
  initHeadServo();
  initLedMatrix();

  // 7. Signal readiness over serial
  Serial.println("ESP32 READY");
}

void loop() {
  // Non-blocking LED mouth animation frame renderer
  updateMouthAnimation();

  // 1. Check Wi-Fi state. If dropped, reconnect immediately
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
    return;
  }

  // 2. Check WebSocket state. If server went down, attempt connection non-blockingly
  if (!wsClient.available()) {
    unsigned long now = millis();
    if (now - lastWsConnectAttempt >= wsConnectInterval) {
      lastWsConnectAttempt = now;
      Serial.println("[WS] Server offline. Retrying connection...");
      connectToWebSocket();
    }
  } else {
    // 3. Run WebSocket task loop to process incoming packets
    wsClient.poll();

    // 4. Send a periodic heartbeat JSON packet to keep the socket channel open
    unsigned long now = millis();
    if (now - lastHeartbeat >= heartbeatInterval) {
      lastHeartbeat = now;
      
      StaticJsonDocument<128> heartbeatDoc;
      heartbeatDoc["type"] = "heartbeat";
      
      String payload;
      serializeJson(heartbeatDoc, payload);
      wsClient.send(payload);
    }
  }
  delay(10);
}

/**
 * Handles Wi-Fi connection logic. Blocks setup briefly, but handles drops gracefully.
 */
void connectToWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.print("[WIFI] Connecting to SSID: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WIFI] Connected successfully!");
    Serial.print("[WIFI] IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WIFI ERROR] Connection timed out. Will retry in loop.");
  }
}

/**
 * Initiates client connection to the Python WebSocket server.
 */
void connectToWebSocket() {
  Serial.print("[WS] Connecting to server at ws://");
  Serial.print(WS_SERVER_IP);
  Serial.print(":");
  Serial.println(WS_SERVER_PORT);

  String url = "ws://" + String(WS_SERVER_IP) + ":" + String(WS_SERVER_PORT) + "/";
  bool success = wsClient.connect(url);

  if (success) {
    Serial.println("[WS] Connected to Python server successfully!");
    
    // Transmit initial status report
    StaticJsonDocument<256> statusDoc;
    statusDoc["type"] = "status";
    statusDoc["status"] = "online";
    statusDoc["ip"] = WiFi.localIP().toString();
    
    String payload;
    serializeJson(statusDoc, payload);
    wsClient.send(payload);
  } else {
    Serial.println("[WS ERROR] Connection failed. Will retry...");
  }
}

/**
 * Triggered automatically when the WebSocket client receives a message.
 * Handles both speech requests (HW-104 output) and status requests (Bluetooth mode).
 */
void onMessageCallback(WebsocketsMessage message) {
  String rawData = message.data();
  Serial.print("[WS] Received raw message: ");
  Serial.println(rawData);

  // Parse JSON package
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, rawData);

  if (error) {
    Serial.print("[JSON ERROR] Deserialization failed: ");
    Serial.println(error.c_str());
    return;
  }

  const char* type = doc["type"];
  if (!type) return;

  // Case 1: Speech command (Direct play on HW-104 speaker)
  if (strcmp(type, "speech") == 0) {
    int msgId = doc["id"];
    const char* text = doc["text"];

    if (text) {
      // 1. Immediately send ACK to Python so it knows message was received
      StaticJsonDocument<128> ackDoc;
      ackDoc["type"] = "ack";
      ackDoc["id"] = msgId;
      
      String ackPayload;
      serializeJson(ackDoc, ackPayload);
      wsClient.send(ackPayload);

      // 2. Play synthesized voice through the 2ohm speaker
      speakText(text);
    }
  }
  
  // Case 2: Status trigger (Laptop Bluetooth speaker mode)
  else if (strcmp(type, "status") == 0) {
    const char* action = doc["action"];
    if (action) {
      Serial.print("[STATUS ACTION] Robot state changed to: ");
      Serial.println(action);
      
      if (strcmp(action, "speaking") == 0) {
        // Speech started on server - trigger real-time LED mouth matrix animation
        const char* text = doc["text"];
        Serial.print("[SPEAKING ON LAPTOP] \"");
        Serial.print(text);
        Serial.println("\"");
        isSpeakingMouth = true;
      } else if (strcmp(action, "idle") == 0) {
        Serial.println("[IDLE] Waiting for next query...");
        isSpeakingMouth = false;
        drawMouthFrame(frameRow2Col4);
      }
    }
  }
  
  // Case 3: HMI control actions (Chassis directions, speed, head sweep angle, tracking toggles)
  else if (strcmp(type, "control") == 0) {
    // 1. Check movement command
    if (doc.containsKey("command")) {
      const char* command = doc["command"];
      driveRobot(command, currentSpeed);
    }
    
    // 2. Check drive speed settings
    if (doc.containsKey("speed")) {
      currentSpeed = doc["speed"];
      Serial.print("[SPEED CONFIG] Drive speed updated to: ");
      Serial.print(currentSpeed);
      Serial.println("%");
    }
    
    // 3. Check head rotation angle
    if (doc.containsKey("head")) {
      currentHeadAngle = doc["head"];
      setHeadAngle(currentHeadAngle);
    }
    
    // 4. Check servo tracking state
    if (doc.containsKey("servo")) {
      isServoTracking = doc["servo"];
      toggleServoTracking(isServoTracking);
    }
  }
}

/**
 * Triggered automatically on WebSocket connection events.
 */
void onEventsCallback(WebsocketsEvent event, String data) {
  if (event == WebsocketsEvent::ConnectionClosed) {
    Serial.println("[WS] Connection lost or closed by server.");
  }
}

/**
 * Offline SAM audio generation logic (HW-104 Output).
 */
void speakText(const String &text) {
  Serial.print("Speaking text offline: ");
  Serial.println(text);

  // Instantiate the speech synthesis engine on the heap
  ESP8266SAM *sam = new ESP8266SAM();
  sam->SetSpeed(72);  // Keep speech rate natural
  sam->SetPitch(64);  // Robotic pitch

  // Workaround space padding to clear DMA audio buffers cleanly
  String speechString = text + " ";

  // Blocks execution until speaking finishes (prevents word overlap)
  sam->Say(audioOut, speechString.c_str());

  // Free memory
  delete sam;
  audioOut->stop();
}

inline void setMotorPwm(int leftDuty, int rightDuty) {
#ifdef ESP8266
  analogWrite(PWM_LEFT_EN, map(leftDuty, 0, 255, 0, 1023));
  analogWrite(PWM_RIGHT_EN, map(rightDuty, 0, 255, 0, 1023));
#else
  ledcWrite(LEDC_LEFT_CHANNEL, leftDuty);
  ledcWrite(LEDC_RIGHT_CHANNEL, rightDuty);
#endif
}

inline void writeServoPulse(int degrees) {
#ifdef ESP8266
  analogWrite(SERVO_ROTATION_PIN, map(degrees, 0, 180, 25, 125));
#else
  int duty = map(degrees, 0, 180, 102, 512); 
  ledcWrite(LEDC_SERVO_CHANNEL, duty);
#endif
}

/**
 * Initializes pins and PWM timers for dual DC motor drivers (L298N/TB6612).
 */
void initChassisMotors() {
  pinMode(MOTOR_LEFT_IN1, OUTPUT);
  pinMode(MOTOR_LEFT_IN2, OUTPUT);
  pinMode(MOTOR_RIGHT_IN3, OUTPUT);
  pinMode(MOTOR_RIGHT_IN4, OUTPUT);
  
  digitalWrite(MOTOR_LEFT_IN1, LOW);
  digitalWrite(MOTOR_LEFT_IN2, LOW);
  digitalWrite(MOTOR_RIGHT_IN3, LOW);
  digitalWrite(MOTOR_RIGHT_IN4, LOW);

#ifndef ESP8266
  // Setup Left & Right speed control PWM signals using ESP32 LEDC (5kHz, 8-bit)
  ledcSetup(LEDC_LEFT_CHANNEL, 5000, 8);
  ledcAttachPin(PWM_LEFT_EN, LEDC_LEFT_CHANNEL);
  
  ledcSetup(LEDC_RIGHT_CHANNEL, 5000, 8);
  ledcAttachPin(PWM_RIGHT_EN, LEDC_RIGHT_CHANNEL);
#endif
  
  setMotorPwm(0, 0);
  Serial.println("[ACTUATING] DC Chassis Motor drivers initialized.");
}

/**
 * Configures the PWM channel for head rotation servo sweep.
 */
void initHeadServo() {
#ifndef ESP8266
  ledcSetup(LEDC_SERVO_CHANNEL, 50, 12);
  ledcAttachPin(SERVO_ROTATION_PIN, LEDC_SERVO_CHANNEL);
#endif
  setHeadAngle(90); // Center head rotation on startup
  Serial.println("[ACTUATING] Head sweep rotation servo initialized.");
}

/**
 * Actuates BTS7960 High-Current DC Motor Drivers based on target steering commands and speeds.
 * Control pins:
 * MOTOR_LEFT_IN1  = L_PWM_FWD (Left Forward PWM)
 * MOTOR_LEFT_IN2  = L_PWM_REV (Left Reverse PWM)
 * MOTOR_RIGHT_IN3 = R_PWM_FWD (Right Forward PWM)
 * MOTOR_RIGHT_IN4 = R_PWM_REV (Right Reverse PWM)
 */
void driveRobot(const String &cmd, int speedPercent) {
  // Motor Dead-Zone Compensation: floor non-zero speeds at PWM duty 70 to overcome static friction
  int duty = (speedPercent == 0) ? 0 : map(speedPercent, 1, 100, 70, 255);
  int pwmVal = map(duty, 0, 255, 0, 1023); // Scale to 10-bit PWM for ESP8266

  Serial.print("[BTS7960] Driving ");
  Serial.print(cmd);
  Serial.print(" at speed ");
  Serial.print(speedPercent);
  Serial.println("%");

  if (cmd.equals("up")) {
    analogWrite(MOTOR_LEFT_IN1, pwmVal);
    analogWrite(MOTOR_LEFT_IN2, 0);
    analogWrite(MOTOR_RIGHT_IN3, pwmVal);
    analogWrite(MOTOR_RIGHT_IN4, 0);
  } 
  else if (cmd.equals("down")) {
    analogWrite(MOTOR_LEFT_IN1, 0);
    analogWrite(MOTOR_LEFT_IN2, pwmVal);
    analogWrite(MOTOR_RIGHT_IN3, 0);
    analogWrite(MOTOR_RIGHT_IN4, pwmVal);
  } 
  else if (cmd.equals("left")) {
    analogWrite(MOTOR_LEFT_IN1, 0);
    analogWrite(MOTOR_LEFT_IN2, pwmVal);
    analogWrite(MOTOR_RIGHT_IN3, pwmVal);
    analogWrite(MOTOR_RIGHT_IN4, 0);
  } 
  else if (cmd.equals("right")) {
    analogWrite(MOTOR_LEFT_IN1, pwmVal);
    analogWrite(MOTOR_LEFT_IN2, 0);
    analogWrite(MOTOR_RIGHT_IN3, 0);
    analogWrite(MOTOR_RIGHT_IN4, pwmVal);
  } 
  else if (cmd.equals("stop")) {
    analogWrite(MOTOR_LEFT_IN1, 0);
    analogWrite(MOTOR_LEFT_IN2, 0);
    analogWrite(MOTOR_RIGHT_IN3, 0);
    analogWrite(MOTOR_RIGHT_IN4, 0);
  }
}

/**
 * Sweeps the head rotation servo using hardware PWM duty mappings.
 */
void setHeadAngle(int degrees) {
  degrees = constrain(degrees, 0, 180);
  writeServoPulse(degrees);
  
  Serial.print("[ACTUATING] Head rotation servo set to ");
  Serial.print(degrees);
  Serial.println(" degrees.");
}

/**
 * Toggles tracking state variables.
 */
void toggleServoTracking(bool enabled) {
  Serial.print("[ACTUATING] Servo Tracking Mode set to: ");
  Serial.println(enabled ? "ON" : "OFF");
}

/**
 * Writes 16-bit register and data payload to all cascaded MAX7219 modules.
 */
void max7219_send_all(byte reg, byte data) {
  digitalWrite(LED_MATRIX_CS, LOW);
  for (int i = 0; i < LED_MATRIX_COUNT; i++) {
    shiftOut(LED_MATRIX_DIN, LED_MATRIX_CLK, MSBFIRST, reg);
    shiftOut(LED_MATRIX_DIN, LED_MATRIX_CLK, MSBFIRST, data);
  }
  digitalWrite(LED_MATRIX_CS, HIGH);
}

/**
 * Writes row byte to a specific module in the cascaded MAX7219 chain.
 */
void max7219_set_row(int module, int row, byte data) {
  digitalWrite(LED_MATRIX_CS, LOW);
  for (int i = 0; i < LED_MATRIX_COUNT; i++) {
    if (i == (LED_MATRIX_COUNT - 1 - module)) {
      shiftOut(LED_MATRIX_DIN, LED_MATRIX_CLK, MSBFIRST, row + 1);
      shiftOut(LED_MATRIX_DIN, LED_MATRIX_CLK, MSBFIRST, data);
    } else {
      shiftOut(LED_MATRIX_DIN, LED_MATRIX_CLK, MSBFIRST, 0x00);
      shiftOut(LED_MATRIX_DIN, LED_MATRIX_CLK, MSBFIRST, 0x00);
    }
  }
  digitalWrite(LED_MATRIX_CS, HIGH);
}

/**
 * Initializes MAX7219 4-in-1 cascaded LED matrix modules for mouth display.
 */
void initLedMatrix() {
  pinMode(LED_MATRIX_DIN, OUTPUT);
  pinMode(LED_MATRIX_CLK, OUTPUT);
  pinMode(LED_MATRIX_CS, OUTPUT);
  digitalWrite(LED_MATRIX_CS, HIGH);

  randomSeed(analogRead(0));

  max7219_send_all(0x0C, 0x01); // Normal operation (shutdown = false)
  max7219_send_all(0x09, 0x00); // No decode
  max7219_send_all(0x0B, 0x07); // Scan limit: 8 rows
  max7219_send_all(0x0A, 0x08); // Medium-high brightness (0-15)

  // Clear display
  for (int r = 0; r < 8; r++) {
    max7219_send_all(r + 1, 0x00);
  }

  // Render neutral resting mouth on initialization
  drawMouthFrame(frameRow2Col4);
  Serial.println("[MOUTH DISPLAY] Native ESP32 MAX7219 4-in-1 driver initialized.");
}

/**
 * Non-blocking animation loop tick that updates the mouth frame when speaking.
 */
void updateMouthAnimation() {
  if (isSpeakingMouth) {
    unsigned long now = millis();
    if (now - lastMouthFrameTime >= currentMouthInterval) {
      lastMouthFrameTime = now;
      
      int nextFrame = random(1, 4);
      switch (nextFrame) {
        case 1: drawMouthFrame(frameRow4Col4); break; // Small open
        case 2: drawMouthFrame(frameRow3Col2); break; // Medium open
        case 3: drawMouthFrame(frameRow3Col3); break; // Wide open
      }
      
      // Natural human speech timing per phoneme (70ms - 160ms)
      currentMouthInterval = random(70, 160);
    }
  }
}

/**
 * Draws an 8x32 mouth frame across 4 cascaded MAX7219 LED modules.
 */
void drawMouthFrame(byte frame[8][4]) {
  for (int row = 0; row < 8; row++) {
    for (int module = 0; module < 4; module++) {
      max7219_set_row(module, row, frame[row][module]);
    }
  }
}

