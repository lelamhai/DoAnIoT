#define PIR_PIN    27    // PIR OUT nối vào D4
#define RELAY_PIN  26    // Relay IN nối vào D2

void setup() {
  Serial.begin(115200);

  pinMode(PIR_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);

  // Tắt relay ban đầu
  digitalWrite(RELAY_PIN, LOW);

  Serial.println("System ready...");
}

void loop() {
  int motionDetected = digitalRead(PIR_PIN);

  if (motionDetected == HIGH) {
    Serial.println("Motion detected -> Speaker ON");
    digitalWrite(RELAY_PIN, HIGH);   // bật relay → loa kêu
  } else {
    Serial.println("No motion -> Speaker OFF");
    digitalWrite(RELAY_PIN, LOW);    // tắt relay → loa tắt
  }

  delay(200); // chống nhiễu PIR
}
