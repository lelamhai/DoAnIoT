/*
  ESP32 + PIR -> MQTT Publisher
  - PIR OUT -> GPIO27
  - Khi PIR HIGH -> publish JSON: {"timestamp": "...", "motion": 1}
  - Khi PIR LOW  -> publish JSON: {"timestamp": "...", "motion": 0}
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <time.h>

/* ===== WIFI ===== */
const char* WIFI_SSID     = "Hoang Minh";
const char* WIFI_PASSWORD = "99999999";

/* ===== MQTT ===== */
const char* mqtt_broker = "broker.hivemq.com";
const int   mqtt_port   = 1883;

// Topic & Client ID theo yêu cầu của bạn
const char* mqtt_topic_motion = "iot/nhom03/security/pir";
String mqtt_client_id = "ESP32_SERCURITY";

/* ===== NTP TIME ===== */
const char* ntp_server = "pool.ntp.org";
const long  gmt_offset_sec = 7 * 3600;  // GMT+7 (Vietnam)
const int   daylight_offset_sec = 0;

/* ===== HARDWARE ===== */
#define PIR_PIN 27   // PIR OUT -> GPIO27

WiFiClient espClient;
PubSubClient client(espClient);

/* ===== STATE ===== */
int lastPirState = -1;
unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL = 500; // ms

/* ===== WIFI CONNECT ===== */
void connectWiFi() {
  Serial.print("Connecting WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print(".");
  }

  Serial.println();
  Serial.print("WiFi connected. IP: ");
  Serial.println(WiFi.localIP());
}

/* ===== MQTT CONNECT ===== */
void connectMQTT() {
  client.setServer(mqtt_broker, mqtt_port);

  Serial.print("Connecting MQTT as ");
  Serial.println(mqtt_client_id);

  while (!client.connected()) {
    if (client.connect(mqtt_client_id.c_str())) {
      Serial.println("MQTT connected");
      
      // Gửi JSON online message
      String json = "{\"timestamp\":\"";
      json += getTimestamp();
      json += "\",\"status\":\"online\"}";
      client.publish(mqtt_topic_motion, json.c_str());
      
    } else {
      Serial.print("MQTT failed, rc=");
      Serial.print(client.state());
      Serial.println(" retry in 2s");
      delay(2000);
    }
  }
}

/* ===== GET TIMESTAMP ===== */
String getTimestamp() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    // Nếu chưa sync NTP, dùng millis
    unsigned long ms = millis();
    char buffer[30];
    sprintf(buffer, "uptime_%lu", ms/1000);
    return String(buffer);
  }
  
  char buffer[30];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  return String(buffer);
}

/* ===== PUBLISH ===== */
void publishMotion(int motionValue) {
  // Tạo JSON: {"timestamp": "2025-09-10T09:30:00Z", "motion": 1}
  String json = "{\"timestamp\":\"";
  json += getTimestamp();
  json += "\",\"motion\":";
  json += String(motionValue);
  json += "}";
  
  bool ok = client.publish(mqtt_topic_motion, json.c_str());

  Serial.print("Publish ");
  Serial.print(ok ? "OK" : "FAIL");
  Serial.print(" -> ");
  Serial.print(mqtt_topic_motion);
  Serial.print(" : ");
  Serial.println(json);
}

/* ===== SETUP ===== */
void setup() {
  Serial.begin(115200);
  delay(500);
  pinMode(PIR_PIN, INPUT);

  Serial.println("================================");
  Serial.println("   ESP32 PIR -> MQTT Publisher");
  Serial.println("================================");
  Serial.print("Client ID: ");
  Serial.println(mqtt_client_id);
  Serial.print("Topic: ");
  Serial.println(mqtt_topic_motion);
  Serial.println("PIR warm-up 30-60s...");
  Serial.println("================================");
  connectWiFi();
  
  // Cấu hình NTP
  Serial.println("Configuring NTP...");
  configTime(gmt_offset_sec, daylight_offset_sec, ntp_server);
  Serial.println("Waiting for NTP sync...");
  delay(2000);  // Đợi sync thời gian
  
  connectMQTT();
}

/* ===== LOOP ===== */
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi lost -> reconnect");
    connectWiFi();
  }

  if (!client.connected()) {
    Serial.println("MQTT lost -> reconnect");
    connectMQTT();
  }

  client.loop();

  int pirState = digitalRead(PIR_PIN);

  if (pirState != lastPirState && millis() - lastSend > SEND_INTERVAL) {
    lastPirState = pirState;
    lastSend = millis();

    if (pirState == HIGH) {
      publishMotion(1);  // motion = 1
    } else {
      publishMotion(0);  // motion = 0
    }
  }

  delay(50);
}
