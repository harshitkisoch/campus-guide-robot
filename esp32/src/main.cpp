/**
 * Campus Guide Robot - Phase 4 Optimized Firmware
 * WebSocket Client implementation. Connects wirelessly to Python WebSocket server.
 * Listens for JSON status and command packets. Routes speech playback to laptop-paired Bluetooth.
 * Prepares structure for future motor and gesture controls.
 */

#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>
#include "wifi_credentials.h"

using namespace websockets;

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

void setup() {
  // 1. Initialize Serial debugging at 115200 baud
  Serial.begin(115200);
  delay(500);

  // 2. Connect to the local Wi-Fi router
  connectToWiFi();

  // 3. Configure WebSocket callbacks for message reception and status changes
  wsClient.onMessage(onMessageCallback);
  wsClient.onEvent(onEventsCallback);

  // 4. Attempt initial connection to Python WebSocket server
  connectToWebSocket();

  // 5. Signal readiness over serial
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
 * Decodes status triggers and prepares for future motor/gesture controls.
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
  
  // Handle status packets (e.g., robot speaking status)
  if (type && strcmp(type, "status") == 0) {
    const char* action = doc["action"];
    if (action) {
      Serial.print("[STATUS ACTION] Robot state changed to: ");
      Serial.println(action);
      
      if (strcmp(action, "speaking") == 0) {
        // Speech started - print text being spoken
        const char* text = doc["text"];
        Serial.print("[SPEAKING TEXT] \"");
        Serial.print(text);
        Serial.println("\"");
        
        // FUTURE: Start eye/mouth LED animations here
      } else if (strcmp(action, "idle") == 0) {
        Serial.println("[IDLE] Waiting for next query...");
        // FUTURE: Stop animations here
      }
    }
  }
  
  // FUTURE: Handle motor commands (e.g., {"type": "motor", "command": "forward"})
  else if (type && strcmp(type, "motor") == 0) {
    const char* command = doc["command"];
    Serial.print("[MOTOR COMMAND] Excuting: ");
    Serial.println(command);
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
