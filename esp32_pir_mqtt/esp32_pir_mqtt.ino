/*
 * ESP32 + PIR Sensor - MQTT Face Recognition Control
 * Nhóm 03 - IoT Project
 * 
 * Chức năng:
 * - PIR phát hiện chuyển động → Gửi "1" lên MQTT
 * - PIR không phát hiện → Gửi "0" lên MQTT
 * - Python app nhận message để điều khiển biến active
 * 
 * Kết nối:
 * - PIR OUT → GPIO 13
 * - PIR VCC → 5V
 * - PIR GND → GND
 */

#include <WiFi.h>
#include <PubSubClient.h>

// ===== WiFi Configuration =====
const char* ssid = "Hoang Minh";           // Thay bằng tên WiFi của bạn
const char* password = "99999999";   // Thay bằng mật khẩu WiFi

// ===== MQTT Configuration =====
const char* mqtt_server = "broker.hivemq.com"; // Public MQTT broker
const int mqtt_port = 1883;
const char* mqtt_client_id = "ESP32_PIR_Nhom03";
const char* mqtt_topic_pir = "iot/nhom03/security/pir";       // Topic gửi PIR state
const char* mqtt_topic_buzzer = "iot/nhom03/security/buzzer"; // Topic nhận lệnh bật loa

// ===== PIR Sensor Configuration =====
const int PIR_PIN = 27;           // GPIO 27 cho PIR sensor
const int RELAY_PIN = 26;         // GPIO 26 cho Relay (điều khiển loa)
const int LED_PIN = 2;            // LED built-in để debug
const int DEBOUNCE_TIME = 500;    // 500ms debounce
const int PUBLISH_INTERVAL = 1000; // Gửi message mỗi 1 giây

// ===== Global Variables =====
WiFiClient espClient;
PubSubClient client(espClient);

int currentPIRState = LOW;
int lastPIRState = LOW;
unsigned long lastDebounceTime = 0;
unsigned long lastPublishTime = 0;

// Relay control
int relayState = LOW;  // LOW = tắt loa, HIGH = bật loa

// ===== Function Prototypes =====
void setup_wifi();
void reconnect_mqtt();
void callback(char* topic, byte* payload, unsigned int length);

void setup() {
  // Khởi tạo Serial
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n\n=================================");
  Serial.println("ESP32 PIR MQTT - Nhom 03");
  Serial.println("=================================");
  
  // Cấu hình GPIO
  pinMode(PIR_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);  // Tắt loa ban đầu
  digitalWrite(LED_PIN, LOW);
  
  Serial.println("✅ GPIO configured");
  Serial.printf("   PIR Pin: GPIO %d\n", PIR_PIN);
  Serial.printf("   Relay Pin: GPIO %d\n", RELAY_PIN);
  Serial.printf("   LED Pin: GPIO %d\n", LED_PIN);
  
  // Kết nối WiFi
  setup_wifi();
  
  // Cấu hình MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial.println("\n⏳ PIR warming up (30s)...");
  delay(30000); // PIR sensor warm-up time
  Serial.println("✅ PIR ready!");
  
  Serial.println("\n=================================");
  Serial.println("🚀 System Ready");
  Serial.println("=================================\n");
}

void loop() {
  // Đảm bảo kết nối MQTT
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();
  
  // Đọc PIR sensor với debounce
  int reading = digitalRead(PIR_PIN);
  
  // Nếu trạng thái PIR thay đổi, reset debounce timer
  if (reading != lastPIRState) {
    lastDebounceTime = millis();
  }
  
  // Chỉ cập nhật sau khi vượt qua debounce time
  if ((millis() - lastDebounceTime) > DEBOUNCE_TIME) {
    // Nếu trạng thái thực sự thay đổi
    if (reading != currentPIRState) {
      currentPIRState = reading;
      
      // Publish message ngay khi phát hiện thay đổi
      const char* message = (currentPIRState == HIGH) ? "1" : "0";
      
      if (client.publish(mqtt_topic_pir, message)) {
        // LED indicator
        digitalWrite(LED_PIN, currentPIRState);
        
        // Log to Serial
        Serial.println("─────────────────────────────────");
        Serial.printf("📡 PIR State Changed: %s\n", (currentPIRState == HIGH) ? "MOTION" : "NO MOTION");
        Serial.printf("📤 Published to MQTT: '%s'\n", message);
        Serial.printf("⏰ Time: %lu ms\n", millis());
        Serial.println("─────────────────────────────────\n");
      } else {
        Serial.println("❌ MQTT publish failed!");
      }
      
      lastPublishTime = millis();
    }
  }
  
  // Publish định kỳ để maintain state (mỗi 1 giây)
  if (millis() - lastPublishTime > PUBLISH_INTERVAL) {
    const char* message = (currentPIRState == HIGH) ? "1" : "0";
    
    if (client.publish(mqtt_topic_pir, message)) {
      Serial.printf("🔄 Heartbeat: PIR=%s\n", message);
    }
    
    lastPublishTime = millis();
  }
  
  lastPIRState = reading;
  
  delay(50); // Small delay for stability
}

void setup_wifi() {
  Serial.println("\n📶 Connecting to WiFi...");
  Serial.printf("   SSID: %s\n", ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempts++;
    
    if (attempts > 40) { // 20 seconds timeout
      Serial.println("\n❌ WiFi connection failed!");
      Serial.println("🔄 Restarting ESP32...");
      ESP.restart();
    }
  }
  
  Serial.println("\n✅ WiFi connected!");
  Serial.printf("   IP Address: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("   Signal: %d dBm\n", WiFi.RSSI());
}

void reconnect_mqtt() {
  // Loop until reconnected
  while (!client.connected()) {
    Serial.println("\n📡 Connecting to MQTT broker...");
    Serial.printf("   Broker: %s:%d\n", mqtt_server, mqtt_port);
    Serial.printf("   Client ID: %s\n", mqtt_client_id);
    
    // Attempt to connect
    if (client.connect(mqtt_client_id)) {
      Serial.println("✅ MQTT connected!");
      
      // Subscribe to buzzer topic (nhận lệnh từ Python)
      client.subscribe(mqtt_topic_buzzer);
      Serial.printf("   📥 Subscribed to: %s\n", mqtt_topic_buzzer);
      Serial.printf("   📤 Publishing to: %s\n", mqtt_topic_pir);
      
      // Publish initial PIR state
      const char* initial_state = (digitalRead(PIR_PIN) == HIGH) ? "1" : "0";
      client.publish(mqtt_topic_pir, initial_state);
      Serial.printf("📤 Initial PIR state published: %s\n", initial_state);
      
    } else {
      Serial.print("❌ MQTT connection failed, rc=");
      Serial.print(client.state());
      Serial.println(" - Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Callback khi nhận message từ Python
  Serial.print("📥 Message received on topic: ");
  Serial.println(topic);
  
  // Convert payload to string
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.printf("   Payload: %s\n", message.c_str());
  
  // Xử lý lệnh buzzer/loa
  if (String(topic) == mqtt_topic_buzzer) {
    if (message == "1") {
      // Bật loa cảnh báo
      digitalWrite(RELAY_PIN, HIGH);
      relayState = HIGH;
      Serial.println("🔊 Relay ON - LOA CẢNH BÁO BẬT!");
    } 
    else if (message == "0") {
      // Tắt loa
      digitalWrite(RELAY_PIN, LOW);
      relayState = LOW;
      Serial.println("🔇 Relay OFF - Loa tắt");
    }
    else {
      Serial.printf("⚠️  Unknown buzzer command: %s\n", message.c_str());
    }
  }
}
