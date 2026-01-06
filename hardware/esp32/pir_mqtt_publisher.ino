/*
 * ESP32 PIR Motion Sensor + MQTT Publisher
 * 
 * Hardware:
 * - PIR HC-SR501 → GPIO 27
 * - Relay Module → GPIO 26
 * 
 * Features:
 * - WiFi connection
 * - MQTT publish motion events
 * - Relay control for alarm/speaker
 * - Auto-reconnect WiFi & MQTT
 * 
 * Author: IoT Security Project Team
 * Date: January 6, 2026
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <time.h>

// ==================== CONFIGURATION ====================
// Pin Definitions
#define PIR_PIN    27    // PIR sensor output → GPIO27
#define RELAY_PIN  26    // Relay control for alarm → GPIO26

// WiFi Credentials (ĐÃ CẤU HÌNH)
const char* WIFI_SSID = "Hoang Minh";      // Tên WiFi
const char* WIFI_PASSWORD = "99999999";    // Mật khẩu WiFi

// MQTT Broker Settings (ĐÃ CẤU HÌNH CHO NHÓM 03)
const char* MQTT_BROKER = "test.mosquitto.org";    // Public MQTT broker
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC = "iot/security/pir/nhom03";  // Topic cho nhóm 03
const char* MQTT_CLIENT_ID = "ESP32_Nhom03_HoangMinh";  // Client ID unique

// NTP Server for timestamp
const char* NTP_SERVER = "pool.ntp.org";
const long GMT_OFFSET = 7 * 3600;  // GMT+7 for Vietnam
const int DAYLIGHT_OFFSET = 0;

// Timing
const unsigned long PUBLISH_INTERVAL = 200;  // milliseconds
const unsigned long RECONNECT_DELAY = 5000;   // milliseconds

// ==================== GLOBAL OBJECTS ====================
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// State variables
int lastMotionState = LOW;
unsigned long lastPublishTime = 0;
unsigned long lastReconnectAttempt = 0;

// ==================== FUNCTION PROTOTYPES ====================
void setupWiFi();
void setupMQTT();
void reconnectWiFi();
void reconnectMQTT();
void publishMotionEvent(int motion);
String getTimestamp();
void handleMotion();

// ==================== SETUP ====================
void setup() {
  // Initialize Serial
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\n=================================");
  Serial.println("ESP32 IoT Security System");
  Serial.println("=================================\n");

  // Configure Pins
  pinMode(PIR_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);  // Turn off relay initially
  Serial.println("✓ GPIO pins configured");

  // Setup WiFi
  setupWiFi();

  // Setup MQTT
  setupMQTT();

  // Initialize time
  configTime(GMT_OFFSET, DAYLIGHT_OFFSET, NTP_SERVER);
  Serial.println("✓ NTP time configured");

  Serial.println("\n✓ System ready!\n");
}

// ==================== MAIN LOOP ====================
void loop() {
  // Ensure WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    reconnectWiFi();
  }

  // Ensure MQTT connection
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }

  // Process MQTT messages
  mqttClient.loop();

  // Handle motion detection
  handleMotion();

  // Small delay to prevent flooding
  delay(50);
}

// ==================== WIFI FUNCTIONS ====================
void setupWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connected!");
    Serial.print("  IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("  Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\n✗ WiFi connection failed!");
    Serial.println("  Please check SSID and password");
  }
}

void reconnectWiFi() {
  if (millis() - lastReconnectAttempt > RECONNECT_DELAY) {
    lastReconnectAttempt = millis();
    Serial.println("Reconnecting to WiFi...");
    WiFi.disconnect();
    WiFi.reconnect();
  }
}

// ==================== MQTT FUNCTIONS ====================
void setupMQTT() {
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  Serial.print("MQTT Broker: ");
  Serial.print(MQTT_BROKER);
  Serial.print(":");
  Serial.println(MQTT_PORT);
  Serial.print("MQTT Topic: ");
  Serial.println(MQTT_TOPIC);
}

void reconnectMQTT() {
  if (millis() - lastReconnectAttempt > RECONNECT_DELAY) {
    lastReconnectAttempt = millis();

    Serial.print("Connecting to MQTT broker... ");

    if (mqttClient.connect(MQTT_CLIENT_ID)) {
      Serial.println("✓ Connected!");
      
      // Publish initial message
      String payload = "{\"timestamp\":\"" + getTimestamp() + 
                      "\",\"motion\":0,\"status\":\"online\"}";
      mqttClient.publish(MQTT_TOPIC, payload.c_str());
      
    } else {
      Serial.print("✗ Failed! RC=");
      Serial.println(mqttClient.state());
    }
  }
}

// ==================== MOTION HANDLING ====================
void handleMotion() {
  int currentMotionState = digitalRead(PIR_PIN);
  unsigned long currentTime = millis();

  // Check if state changed or publish interval elapsed
  bool stateChanged = (currentMotionState != lastMotionState);
  bool intervalElapsed = (currentTime - lastPublishTime >= PUBLISH_INTERVAL);

  if (stateChanged || (currentMotionState == HIGH && intervalElapsed)) {
    
    // Control relay based on motion
    if (currentMotionState == HIGH) {
      digitalWrite(RELAY_PIN, HIGH);  // Activate alarm
      Serial.println("🔴 MOTION DETECTED!");
    } else {
      digitalWrite(RELAY_PIN, LOW);   // Deactivate alarm
      Serial.println("🟢 No motion");
    }

    // Publish to MQTT
    if (mqttClient.connected()) {
      publishMotionEvent(currentMotionState);
      lastPublishTime = currentTime;
    }

    lastMotionState = currentMotionState;
  }
}

void publishMotionEvent(int motion) {
  // Create JSON payload
  String payload = "{";
  payload += "\"timestamp\":\"" + getTimestamp() + "\",";
  payload += "\"motion\":" + String(motion) + ",";
  payload += "\"sensor_id\":\"" + String(MQTT_CLIENT_ID) + "\",";
  payload += "\"location\":\"living_room\"";
  payload += "}";

  // Publish to MQTT
  bool success = mqttClient.publish(MQTT_TOPIC, payload.c_str());

  if (success) {
    Serial.print("📤 Published: ");
    Serial.println(payload);
  } else {
    Serial.println("✗ Publish failed!");
  }
}

// ==================== UTILITY FUNCTIONS ====================
String getTimestamp() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "2026-01-06T00:00:00Z";  // Fallback
  }

  char buffer[30];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  return String(buffer);
}
