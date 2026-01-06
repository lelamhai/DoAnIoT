# 🔌 ESP32 HARDWARE SETUP & TESTING GUIDE

Hướng dẫn chi tiết upload code lên ESP32 và test với PIR sensor thật.

---

## 📋 PREREQUISITES

### Hardware Required:
- ✅ ESP32 DevKit (ESP32-WROOM-32)
- ✅ PIR HC-SR501 Motion Sensor
- ✅ Relay Module (optional, for alarm/light control)
- ✅ Breadboard
- ✅ Jumper wires (Male-to-Male, Male-to-Female)
- ✅ USB Cable (USB-A to Micro-USB)
- ✅ Power supply 5V (or USB power)

### Software Required:
- ✅ Arduino IDE (Version 1.8.19 or 2.x)
- ✅ ESP32 Board Support Package
- ✅ WiFi network (2.4GHz, WPA2)

---

## 🔧 STEP 1: WIRING DIAGRAM

### PIR HC-SR501 to ESP32
```
PIR Sensor          ESP32
──────────────────────────
VCC    (Red)    →  3.3V or 5V
GND    (Black)  →  GND
OUT    (Yellow) →  GPIO 27
```

### Relay Module to ESP32 (Optional)
```
Relay Module        ESP32
──────────────────────────
VCC             →  5V
GND             →  GND
IN              →  GPIO 26
```

### Complete Wiring
```
                 ┌───────────────┐
                 │   ESP32       │
                 │               │
    PIR          │  GPIO 27 ◄────┼──── PIR OUT
 ┌──────┐        │               │
 │ VCC  ├────────┼─► 3.3V        │
 │ GND  ├────────┼─► GND         │
 │ OUT  ├────────┼─► GPIO 27     │
 └──────┘        │               │
                 │  GPIO 26 ─────┼──► Relay IN
    Relay        │               │
 ┌──────┐        │               │
 │ VCC  ├────────┼─► 5V          │
 │ GND  ├────────┼─► GND         │
 │ IN   ├────────┼─► GPIO 26     │
 └──────┘        │               │
                 │               │
                 │  USB ◄────────┼──── Computer
                 └───────────────┘
```

### PIR Sensor Adjustment
**Trên mặt PIR sensor có 2 potentiometers:**
1. **Sensitivity (Sx)**: Khoảng cách phát hiện (3-7m)
2. **Time Delay (Tx)**: Thời gian output HIGH (5s - 300s)

**Recommended Settings:**
- Sensitivity: Vặn vừa phải (4-5m)
- Time Delay: Vặn tối thiểu (5-10s)
- Jumper: H (Retriggerable mode)

---

## 🛠️ STEP 2: INSTALL ARDUINO IDE

### Windows:
1. Download Arduino IDE: https://www.arduino.cc/en/software
2. Install Arduino IDE 2.x
3. Open Arduino IDE

### Add ESP32 Board Support:
1. Go to **File → Preferences**
2. In "Additional Board Manager URLs", add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Click **OK**
4. Go to **Tools → Board → Boards Manager**
5. Search for "ESP32"
6. Install "**esp32 by Espressif Systems**" (Version 2.0.x or 3.0.x)

---

## 📝 STEP 3: CONFIGURE ESP32 CODE

### Open Code:
```bash
# In Arduino IDE:
File → Open → arduino/arduino.ino
```

### Configure WiFi Credentials:
```cpp
// Line 11-12 in arduino.ino
const char* ssid = "Hoang Minh";        // ✅ Already configured
const char* password = "99999999";       // ✅ Already configured
```

### Verify MQTT Settings:
```cpp
// Line 15-16
const char* mqtt_server = "test.mosquitto.org";  // ✅ Correct
const char* mqtt_topic = "iot/security/pir/nhom03";  // ✅ Correct
```

### Verify GPIO Pins:
```cpp
// Line 8-9
#define PIR_PIN 27    // ✅ Correct
#define RELAY_PIN 26  // ✅ Correct
```

**Code is ready! No changes needed.**

---

## ⬆️ STEP 4: UPLOAD CODE TO ESP32

### 1. Connect ESP32:
- Plug USB cable into ESP32
- Connect to computer
- Windows will install drivers automatically

### 2. Select Board:
```
Tools → Board → ESP32 Arduino → ESP32 Dev Module
```

### 3. Select Port:
```
Tools → Port → COM3 (or COM4, COM5, etc.)
```

**How to find correct port:**
- Disconnect ESP32 → Note available ports
- Connect ESP32 → New port appears (that's your ESP32)

### 4. Configure Upload Settings:
```
Tools → Upload Speed → 921600
Tools → Flash Frequency → 80MHz
Tools → Flash Mode → QIO
Tools → Flash Size → 4MB (32Mb)
Tools → Partition Scheme → Default 4MB with spiffs
```

### 5. Compile & Upload:
1. Click **Verify** (✓) button → Wait for compilation
2. If successful, click **Upload** (→) button
3. Wait for upload (takes 10-20 seconds)

**Expected Output:**
```
Sketch uses 256,000 bytes (19%) of program storage space.
Global variables use 16,000 bytes (4%) of dynamic memory.

esptool.py v3.0
Serial port COM3
Connecting........___
Chip is ESP32D0WDQ6 (revision 1)
...
Writing at 0x00010000... (100%)
Wrote 256000 bytes in 3.2 seconds (640.0 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```

✅ **Upload Complete!**

---

## 🔍 STEP 5: VERIFY ESP32 OPERATION

### 1. Open Serial Monitor:
```
Tools → Serial Monitor
Set baud rate to: 115200
```

### 2. Expected Serial Output:
```
=========================================
ESP32 PIR MQTT Publisher - Nhom 03
=========================================

Connecting to WiFi: Hoang Minh
.....
✓ WiFi Connected!
  IP Address: 192.168.1.123
  Signal: -45 dBm

Connecting to MQTT: test.mosquitto.org
✓ MQTT Connected!
  Topic: iot/security/pir/nhom03
  Client ID: ESP32_PIR_nhom03

=========================================
System Ready - Monitoring PIR Sensor
=========================================

[00:00:05] Motion: 0 | Published ✓
[00:00:10] Motion: 0 | Published ✓
[00:00:15] Motion: 1 | 🔴 MOTION DETECTED | Published ✓
[00:00:20] Motion: 1 | 🔴 MOTION DETECTED | Published ✓
```

### 3. Test PIR Sensor:
- Wave your hand in front of PIR sensor
- Serial Monitor should show: "🔴 MOTION DETECTED"
- Relay clicks (if connected)

---

## 🧪 STEP 6: TEST MQTT PUBLISHING

### Method 1: MQTT Subscriber (Command Line)
```bash
# Install mosquitto-clients
# Windows: Download from https://mosquitto.org/download/

# Subscribe to topic
mosquitto_sub -h test.mosquitto.org -t iot/security/pir/nhom03 -v
```

**Expected Output:**
```
iot/security/pir/nhom03 {"timestamp":"2026-01-06T14:30:45","motion":0,"sensor_id":"ESP32_PIR_nhom03","location":"living_room"}
iot/security/pir/nhom03 {"timestamp":"2026-01-06T14:30:50","motion":1,"sensor_id":"ESP32_PIR_nhom03","location":"living_room"}
```

### Method 2: Python MQTT Subscriber
```python
# test_mqtt_receive.py
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"Received: {msg.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message
client.connect("test.mosquitto.org", 1883)
client.subscribe("iot/security/pir/nhom03")
client.loop_forever()
```

```bash
python test_mqtt_receive.py
```

---

## 🔗 STEP 7: END-TO-END TESTING

### 1. Start Backend:
```bash
# Terminal 1
python backend/main.py
```

**Expected:**
```
==================================================
IoT SECURITY MONITORING SYSTEM - BACKEND
==================================================

  ✓ MQTT Config: test.mosquitto.org:1883
  ✓ Database connected: data\security.db
  ✓ CSV Logger initialized
  ✓ AI Service initialized
  ✓ Alert Service initialized

🔄 Waiting for MQTT messages...
```

### 2. Start Dashboard:
```bash
# Terminal 2
streamlit run frontend/app.py
```

### 3. Trigger PIR Sensor:
- Wave hand in front of PIR sensor
- Check all 3 outputs:

**Serial Monitor (ESP32):**
```
[00:05:23] Motion: 1 | 🔴 MOTION DETECTED | Published ✓
```

**Backend Console:**
```
[Event #1] 🔴 ⚠️ 2026-01-06 14:35:23
  Motion: 1 | Sensor: ESP32_PIR_nhom03 | Location: living_room
  AI: SUSPICIOUS (78.5%) | Alert: WARNING
  ✓ Saved to database
  🔔 Alert sent: WARNING
```

**Dashboard (Browser):**
- Current Status: 🔴 MOTION DETECTED
- New row in event table
- Chart updates in real-time
- Statistics increment

✅ **End-to-End Test PASSED!**

---

## 🐛 TROUBLESHOOTING

### Issue 1: ESP32 Not Detected
**Symptoms:** No COM port appears

**Solutions:**
1. Install CP2102 USB driver:
   - Download: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
   - Install and restart computer
2. Try different USB cable (some cables are power-only)
3. Check Device Manager → Ports (COM & LPT)

---

### Issue 2: Upload Failed
**Symptoms:** "Failed to connect to ESP32"

**Solutions:**
1. Hold BOOT button on ESP32 during upload
2. Reduce upload speed: `Tools → Upload Speed → 115200`
3. Press RESET button after upload fails
4. Try different USB port

---

### Issue 3: WiFi Connection Failed
**Symptoms:** "Connecting to WiFi....." (never connects)

**Solutions:**
1. Verify WiFi SSID and password in code
2. Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
3. Check WiFi signal strength
4. Restart router
5. Check Serial Monitor for error messages

---

### Issue 4: MQTT Connection Failed
**Symptoms:** "MQTT connection failed, rc=-2"

**Solutions:**
1. Check internet connection
2. Verify MQTT broker: `test.mosquitto.org`
3. Check firewall (allow port 1883)
4. Try alternative broker:
   ```cpp
   const char* mqtt_server = "broker.hivemq.com";
   ```

---

### Issue 5: PIR Sensor Not Detecting
**Symptoms:** Motion always 0 or always 1

**Solutions:**
1. Check wiring (VCC, GND, OUT)
2. Adjust sensitivity potentiometer
3. Wait 30-60 seconds for PIR to stabilize
4. Check jumper position (should be H)
5. Measure voltage on OUT pin (should toggle 0V/3.3V)

---

## 📊 PERFORMANCE BENCHMARKS

### ESP32 Performance:
- WiFi Connection Time: 5-10 seconds
- MQTT Connection Time: 1-3 seconds
- Publish Interval: 5 seconds (configurable)
- Power Consumption: ~80mA (WiFi active)

### PIR Sensor:
- Detection Range: 3-7 meters
- Detection Angle: 120°
- Response Time: < 1 second
- Stabilization Time: 30-60 seconds after power-on

---

## ✅ TESTING CHECKLIST

Before demo, verify:

- [ ] ESP32 connected to WiFi
- [ ] Serial Monitor shows MQTT messages
- [ ] PIR sensor detects motion reliably
- [ ] MQTT messages received by backend
- [ ] Database updates with new events
- [ ] Dashboard shows real-time updates
- [ ] AI predictions generated
- [ ] Alerts sent (console/email/telegram)
- [ ] Relay activates (if connected)
- [ ] System stable for 5+ minutes

---

## 🎯 DEMO PREPARATION

### Hardware Demo Setup:
1. **Power:** Use USB power bank (portable demo)
2. **Mounting:** Attach ESP32+PIR to board/case
3. **Visibility:** Position PIR sensor facing demo area
4. **Labeling:** Add labels for components
5. **Safety:** Ensure stable wiring

### Demo Flow:
```
1. Show hardware setup (ESP32 + PIR + Relay)
2. Show Serial Monitor output
3. Trigger PIR sensor manually
4. Show MQTT message published
5. Show backend receiving message
6. Show AI prediction
7. Show dashboard update
8. Show alert being sent
```

---

## 📸 PHOTO DOCUMENTATION

**Take photos of:**
1. Complete hardware setup (ESP32 + PIR + Breadboard)
2. Wiring diagram (close-up)
3. Serial Monitor output
4. Dashboard with real-time data
5. Alert notification (email/telegram)

**Use photos for:**
- Final report
- Presentation slides
- Documentation

---

## 🚀 NEXT STEPS AFTER HARDWARE TEST

✅ Hardware working → Proceed to:
1. ✅ Long-term stability test (24 hours)
2. ✅ Performance optimization
3. ✅ Unit tests (Phase 8)
4. ✅ Final documentation
5. ✅ Demo preparation
6. ✅ Presentation slides

---

**Generated:** January 6, 2026  
**Author:** IoT Project Team  
**Status:** Ready for Hardware Testing
