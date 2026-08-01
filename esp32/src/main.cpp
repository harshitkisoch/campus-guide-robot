/**
 * Campus Guide Robot - Phase 5 Hybrid Firmware
 * Supports BOTH:
 * 1. Wireless Acks & speaking status events (for Laptop Bluetooth mode)
 * 2. Wireless Text-to-Speech synthesis using SAM on GPIO 25 (for HW-104 fallback mode)
 * Prepares structure for future motor and gesture controls.
 */

#include <Arduino.h>
#include <WiFi.h>
#include <ESP8266SAM.h>
#include <AudioOutputI2S.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>
#include "wifi_credentials.h"

using namespace websockets;

// --- HMI Hardware Pin Architecture ---
#define MOTOR_LEFT_IN1      16
#define MOTOR_LEFT_IN2      17
#define MOTOR_RIGHT_IN3     18
#define MOTOR_RIGHT_IN4     19
#define PWM_LEFT_EN         14
#define PWM_RIGHT_EN        27
#define SERVO_ROTATION_PIN  13

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

  // 6. Initialize DC Motor outputs & Head Servo
  initChassisMotors();
  initHeadServo();

  // 7. Signal readiness over serial
  Serial.println("ESP32 READY");
}

void loop() {
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
        // Speech started on laptop - print the text being spoken
        const char* text = doc["text"];
        Serial.print("[SPEAKING ON LAPTOP] \"");
        Serial.print(text);
        Serial.println("\"");
        // FUTURE: Start eye/mouth LED animations here
      } else if (strcmp(action, "idle") == 0) {
        Serial.println("[IDLE] Waiting for next query...");
        // FUTURE: Stop animations here
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

/**
 * Initializes pins and LEDC PWM timers for dual DC motor drivers (L298N/TB6612).
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

  // Setup Left & Right speed control PWM signals using ESP32 LEDC (5kHz, 8-bit)
  ledcSetup(LEDC_LEFT_CHANNEL, 5000, 8);
  ledcAttachPin(PWM_LEFT_EN, LEDC_LEFT_CHANNEL);
  
  ledcSetup(LEDC_RIGHT_CHANNEL, 5000, 8);
  ledcAttachPin(PWM_RIGHT_EN, LEDC_RIGHT_CHANNEL);
  
  ledcWrite(LEDC_LEFT_CHANNEL, 0);
  ledcWrite(LEDC_RIGHT_CHANNEL, 0);
  
  Serial.println("[ACTUATING] DC Chassis Motor drivers initialized.");
}

/**
 * Configures the LEDC PWM channel for head rotation servo sweep (50Hz, 12-bit).
 */
void initHeadServo() {
  ledcSetup(LEDC_SERVO_CHANNEL, 50, 12);
  ledcAttachPin(SERVO_ROTATION_PIN, LEDC_SERVO_CHANNEL);
  setHeadAngle(90); // Center head rotation on startup
  Serial.println("[ACTUATING] Head sweep rotation servo initialized.");
}

/**
 * Actuates chassis DC motors based on target steering commands and speeds.
 */
void driveRobot(const String &cmd, int speedPercent) {
  int duty = map(speedPercent, 0, 100, 0, 255);
  Serial.print("[ACTUATING] Driving ");
  Serial.print(cmd);
  Serial.print(" at speed ");
  Serial.print(speedPercent);
  Serial.println("%");

  if (cmd.equals("up")) {
    digitalWrite(MOTOR_LEFT_IN1, HIGH);
    digitalWrite(MOTOR_LEFT_IN2, LOW);
    digitalWrite(MOTOR_RIGHT_IN3, HIGH);
    digitalWrite(MOTOR_RIGHT_IN4, LOW);
    ledcWrite(LEDC_LEFT_CHANNEL, duty);
    ledcWrite(LEDC_RIGHT_CHANNEL, duty);
  } 
  else if (cmd.equals("down")) {
    digitalWrite(MOTOR_LEFT_IN1, LOW);
    digitalWrite(MOTOR_LEFT_IN2, HIGH);
    digitalWrite(MOTOR_RIGHT_IN3, LOW);
    digitalWrite(MOTOR_RIGHT_IN4, HIGH);
    ledcWrite(LEDC_LEFT_CHANNEL, duty);
    ledcWrite(LEDC_RIGHT_CHANNEL, duty);
  } 
  else if (cmd.equals("left")) {
    digitalWrite(MOTOR_LEFT_IN1, LOW);
    digitalWrite(MOTOR_LEFT_IN2, HIGH);
    digitalWrite(MOTOR_RIGHT_IN3, HIGH);
    digitalWrite(MOTOR_RIGHT_IN4, LOW);
    ledcWrite(LEDC_LEFT_CHANNEL, duty);
    ledcWrite(LEDC_RIGHT_CHANNEL, duty);
  } 
  else if (cmd.equals("right")) {
    digitalWrite(MOTOR_LEFT_IN1, HIGH);
    digitalWrite(MOTOR_LEFT_IN2, LOW);
    digitalWrite(MOTOR_RIGHT_IN3, LOW);
    digitalWrite(MOTOR_RIGHT_IN4, HIGH);
    ledcWrite(LEDC_LEFT_CHANNEL, duty);
    ledcWrite(LEDC_RIGHT_CHANNEL, duty);
  } 
  else if (cmd.equals("stop")) {
    digitalWrite(MOTOR_LEFT_IN1, LOW);
    digitalWrite(MOTOR_LEFT_IN2, LOW);
    digitalWrite(MOTOR_RIGHT_IN3, LOW);
    digitalWrite(MOTOR_RIGHT_IN4, LOW);
    ledcWrite(LEDC_LEFT_CHANNEL, 0);
    ledcWrite(LEDC_RIGHT_CHANNEL, 0);
  }
}

/**
 * Sweeps the head rotation servo using pure ESP32 hardware PWM duty mappings.
 */
void setHeadAngle(int degrees) {
  degrees = constrain(degrees, 0, 180);
  // Map 0-180 degrees to 50Hz 12-bit duty values (approx 0.5ms - 2.5ms pulse)
  int duty = map(degrees, 0, 180, 102, 512); 
  ledcWrite(LEDC_SERVO_CHANNEL, duty);
  
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

