/*
 * Arduino PIR Motion Sensor + Serial Output
 * 
 * Hardware:
 * - PIR HC-SR501 → Pin 7
 * - Relay Module → Pin 8
 * 
 * Output: Serial JSON messages
 * Baud Rate: 115200
 * 
 * Note: Dùng với Serial Bridge trên PC để publish MQTT
 * 
 * Author: IoT Security Project Team
 * Date: January 6, 2026
 */

// ==================== PIN DEFINITIONS ====================
#define PIR_PIN    7     // PIR sensor output
#define RELAY_PIN  8     // Relay control for alarm
#define LED_PIN    13    // Built-in LED for status indication

// ==================== TIMING CONFIGURATION ====================
const unsigned long PUBLISH_INTERVAL = 200;  // milliseconds
const unsigned long LED_BLINK_INTERVAL = 1000;  // milliseconds

// ==================== STATE VARIABLES ====================
int lastMotionState = LOW;
unsigned long lastPublishTime = 0;
unsigned long lastLedToggle = 0;
bool ledState = false;
unsigned long messageCount = 0;

// ==================== SETUP ====================
void setup() {
  // Initialize Serial communication
  Serial.begin(115200);
  
  // Wait for Serial to be ready
  while (!Serial && millis() < 3000) {
    ; // Wait max 3 seconds
  }
  
  // Print startup message
  Serial.println();
  Serial.println("========================================");
  Serial.println("Arduino PIR Motion Sensor");
  Serial.println("Serial Output Mode");
  Serial.println("========================================");
  
  // Configure pins
  pinMode(PIR_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Initialize outputs
  digitalWrite(RELAY_PIN, LOW);   // Turn off relay
  digitalWrite(LED_PIN, LOW);     // Turn off LED
  
  Serial.println("Status: READY");
  Serial.println("Format: JSON");
  Serial.println("Baud Rate: 115200");
  Serial.println("========================================");
  Serial.println();
  
  // Wait for PIR sensor to stabilize (30 seconds)
  Serial.println("Waiting for PIR sensor to stabilize...");
  for (int i = 30; i > 0; i--) {
    Serial.print("  ");
    Serial.print(i);
    Serial.println(" seconds remaining");
    delay(1000);
  }
  Serial.println("PIR sensor ready!");
  Serial.println();
}

// ==================== MAIN LOOP ====================
void loop() {
  unsigned long currentTime = millis();
  
  // Read PIR sensor
  int currentMotionState = digitalRead(PIR_PIN);
  
  // Check if state changed or interval elapsed
  bool stateChanged = (currentMotionState != lastMotionState);
  bool intervalElapsed = (currentTime - lastPublishTime >= PUBLISH_INTERVAL);
  
  if (stateChanged || (currentMotionState == HIGH && intervalElapsed)) {
    handleMotionChange(currentMotionState);
    lastPublishTime = currentTime;
    lastMotionState = currentMotionState;
  }
  
  // Blink LED to show system is alive
  if (currentTime - lastLedToggle >= LED_BLINK_INTERVAL) {
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState);
    lastLedToggle = currentTime;
  }
  
  // Small delay
  delay(50);
}

// ==================== MOTION HANDLING ====================
void handleMotionChange(int motion) {
  // Control relay
  if (motion == HIGH) {
    digitalWrite(RELAY_PIN, HIGH);  // Activate alarm
  } else {
    digitalWrite(RELAY_PIN, LOW);   // Deactivate alarm
  }
  
  // Send JSON message via Serial
  sendMotionEvent(motion);
}

void sendMotionEvent(int motion) {
  messageCount++;
  
  // Create JSON payload
  Serial.print("{");
  Serial.print("\"timestamp\":\"");
  Serial.print(getTimestamp());
  Serial.print("\",");
  Serial.print("\"motion\":");
  Serial.print(motion);
  Serial.print(",");
  Serial.print("\"sensor_id\":\"PIR_ARDUINO_001\",");
  Serial.print("\"location\":\"living_room\",");
  Serial.print("\"msg_count\":");
  Serial.print(messageCount);
  Serial.println("}");
}

// ==================== UTILITY FUNCTIONS ====================
String getTimestamp() {
  // Since Arduino doesn't have RTC, use uptime as timestamp
  // Serial Bridge will replace this with actual timestamp
  unsigned long seconds = millis() / 1000;
  unsigned long minutes = seconds / 60;
  unsigned long hours = minutes / 60;
  
  seconds = seconds % 60;
  minutes = minutes % 60;
  
  // Format: UPTIME_HH:MM:SS
  String timestamp = "UPTIME_";
  if (hours < 10) timestamp += "0";
  timestamp += String(hours);
  timestamp += ":";
  if (minutes < 10) timestamp += "0";
  timestamp += String(minutes);
  timestamp += ":";
  if (seconds < 10) timestamp += "0";
  timestamp += String(seconds);
  
  return timestamp;
}
