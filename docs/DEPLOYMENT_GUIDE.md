# 🚀 DEPLOYMENT GUIDE

## IoT Security Monitoring System - Production Deployment

---

## 📋 PREREQUISITES

### Hardware Requirements
- **ESP32 DevKit:** 1x ESP32-WROOM-32
- **PIR Sensor:** 1x HC-SR501
- **Relay Module:** 1x (optional for alarm)
- **Power Supply:** 5V USB or AC adapter
- **Internet:** WiFi connection (2.4GHz)

### Software Requirements
- **Python:** 3.8+ (Recommended: 3.12)
- **Arduino IDE:** 1.8.19+ or 2.x
- **Operating System:** Windows 10/11, Linux, macOS
- **Browser:** Modern browser for dashboard

---

## 🔧 INSTALLATION

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/DoAnIoT.git
cd DoAnIoT
```

### Step 2: Python Environment

#### Option A: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

#### Option B: System-wide
```bash
# Install directly to system Python
pip install -r requirements.txt
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required Packages:**
```
paho-mqtt>=1.6.1
pandas>=2.0.0
scikit-learn>=1.3.0
streamlit>=1.28.0
plotly>=5.17.0
pyyaml>=6.0
psutil>=5.9.0
colorama>=0.4.6
requests>=2.31.0
pytest>=7.4.0
pytest-cov>=4.1.0
```

---

## ⚙️ CONFIGURATION

### 1. MQTT Configuration

Edit `config/mqtt_config.yaml`:

```yaml
mqtt:
  broker: "test.mosquitto.org"
  port: 1883
  topic: "iot/security/pir/nhom03"
  qos: 1
  username: null  # Set if broker requires auth
  password: null
```

**For Production:** Use private broker
```yaml
mqtt:
  broker: "your.mqtt.broker.com"
  port: 8883  # TLS port
  username: "your_username"
  password: "your_password"
  use_tls: true
```

---

### 2. Database Configuration

Edit `config/database_config.yaml`:

```yaml
database:
  path: "data/security.db"
  backup_enabled: true
  backup_path: "data/backups/"
  auto_backup_interval: 3600  # seconds
```

---

### 3. Alert Configuration

Edit `config/alert_config.yaml` or use environment variables:

#### Email Alerts (Gmail)
```bash
# Windows PowerShell
$env:ALERT_EMAIL_ENABLED="true"
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USERNAME="your_email@gmail.com"
$env:SMTP_PASSWORD="your_app_password"
$env:ALERT_RECIPIENTS="admin@example.com,security@example.com"

# Linux/Mac
export ALERT_EMAIL_ENABLED="true"
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your_email@gmail.com"
export SMTP_PASSWORD="your_app_password"
export ALERT_RECIPIENTS="admin@example.com,security@example.com"
```

**Gmail Setup:**
1. Enable 2-Factor Authentication
2. Generate App Password: Google Account → Security → App Passwords
3. Use 16-character password

#### Telegram Alerts
```bash
# Windows
$env:TELEGRAM_ENABLED="true"
$env:TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
$env:TELEGRAM_CHAT_IDS="123456789,987654321"

# Linux/Mac
export TELEGRAM_ENABLED="true"
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
export TELEGRAM_CHAT_IDS="123456789,987654321"
```

**Telegram Setup:**
1. Create bot with @BotFather
2. Send `/newbot` and follow instructions
3. Get Chat ID from `https://api.telegram.org/bot<TOKEN>/getUpdates`

---

### 4. ESP32 Configuration

Edit `arduino/arduino.ino`:

```cpp
// WiFi credentials
const char* ssid = "Your_WiFi_SSID";
const char* password = "Your_WiFi_Password";

// MQTT settings
const char* mqtt_server = "test.mosquitto.org";
const char* mqtt_topic = "iot/security/pir/nhom03";
```

**Upload to ESP32:**
1. Open Arduino IDE
2. File → Open → `arduino/arduino.ino`
3. Tools → Board → ESP32 Dev Module
4. Tools → Port → (Select your port)
5. Click Upload

---

## 🚀 DEPLOYMENT

### Development Environment

#### 1. Start Backend
```bash
python backend/main.py
```

Expected output:
```
==================================================
IoT SECURITY MONITORING SYSTEM - BACKEND
==================================================
  ✓ Database connected: data\security.db
  ✓ AI Service initialized
  ✓ Alert Service initialized
✅ Backend is running!
```

#### 2. Start Dashboard
```bash
streamlit run frontend/app.py
```

Opens in browser: `http://localhost:8501`

---

### Production Deployment

#### Option 1: Systemd Service (Linux)

Create `/etc/systemd/system/iot-backend.service`:

```ini
[Unit]
Description=IoT Security Backend
After=network.target

[Service]
Type=simple
User=iot
WorkingDirectory=/opt/DoAnIoT
Environment="PATH=/opt/DoAnIoT/venv/bin"
ExecStart=/opt/DoAnIoT/venv/bin/python backend/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/iot-dashboard.service`:

```ini
[Unit]
Description=IoT Security Dashboard
After=network.target iot-backend.service

[Service]
Type=simple
User=iot
WorkingDirectory=/opt/DoAnIoT
Environment="PATH=/opt/DoAnIoT/venv/bin"
ExecStart=/opt/DoAnIoT/venv/bin/streamlit run frontend/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl enable iot-backend
sudo systemctl enable iot-dashboard
sudo systemctl start iot-backend
sudo systemctl start iot-dashboard
```

#### Option 2: Docker (Cross-platform)

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["sh", "-c", "python backend/main.py & streamlit run frontend/app.py"]
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    container_name: iot-backend
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - ALERT_EMAIL_ENABLED=${ALERT_EMAIL_ENABLED}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
    restart: unless-stopped
```

**Deploy:**
```bash
docker-compose up -d
```

#### Option 3: Windows Service

Use **NSSM** (Non-Sucking Service Manager):

```bash
# Download NSSM from nssm.cc
# Install backend service
nssm install IoTBackend "C:\Python312\python.exe" "C:\DoAnIoT\backend\main.py"
nssm set IoTBackend AppDirectory "C:\DoAnIoT"
nssm start IoTBackend

# Install dashboard service
nssm install IoTDashboard "C:\Python312\Scripts\streamlit.exe" "run frontend\app.py"
nssm set IoTDashboard AppDirectory "C:\DoAnIoT"
nssm start IoTDashboard
```

---

## 🔒 SECURITY

### 1. MQTT Security

**Production MQTT Broker:**
```yaml
mqtt:
  broker: "secure.broker.com"
  port: 8883  # TLS/SSL port
  username: "iot_client"
  password: "strong_password_here"
  use_tls: true
  ca_cert: "/path/to/ca.crt"
```

### 2. Database Security

```bash
# Set file permissions (Linux)
chmod 600 data/security.db
chown iot:iot data/security.db

# Backup regularly
0 2 * * * /opt/DoAnIoT/scripts/backup_database.sh
```

### 3. API Security (Future)

```python
# Add authentication middleware
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/api/events")
async def get_events(token: str = Depends(security)):
    # Verify token
    if not verify_token(token):
        raise HTTPException(status_code=401)
    return events
```

---

## 📊 MONITORING

### 1. System Health

```bash
# Check backend status
python -c "from backend.infrastructure.system_monitor import SystemMonitor; m = SystemMonitor(); m.print_status()"
```

### 2. Logs

```bash
# View backend logs
tail -f logs/app.log

# View error logs
tail -f logs/errors.log

# View event CSV
tail -f logs/events.csv
```

### 3. Database Maintenance

```bash
# Vacuum database (optimize)
sqlite3 data/security.db "VACUUM;"

# Check database size
du -h data/security.db

# Export events
sqlite3 data/security.db "SELECT * FROM events;" > events_export.csv
```

---

## 🔄 UPDATES

### Update Application

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
systemctl restart iot-backend
systemctl restart iot-dashboard
```

### Update AI Model

```bash
# Retrain model
python ai_model/train.py

# Backup old model
cp ai_model/models/classifier.pkl ai_model/models/classifier_backup.pkl

# Restart backend
systemctl restart iot-backend
```

---

## 🧪 TESTING

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=backend --cov-report=html

# Specific test
pytest tests/test_database.py -v

# Integration tests
python scripts/test_integration.py
```

---

## 📈 SCALING

### Horizontal Scaling

```yaml
# docker-compose-scaled.yml
version: '3.8'

services:
  backend:
    build: .
    deploy:
      replicas: 3  # Multiple backend instances
    ports:
      - "8501-8503:8501"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_timestamp ON events(timestamp);
CREATE INDEX idx_alert_level ON events(alert_level);

-- Archive old events
DELETE FROM events WHERE timestamp < date('now', '-90 days');
```

---

## 🐛 TROUBLESHOOTING

### Backend Won't Start

```bash
# Check Python version
python --version

# Check dependencies
pip list

# Check MQTT connectivity
mosquitto_sub -h test.mosquitto.org -t test/topic
```

### Dashboard Not Loading

```bash
# Check port availability
netstat -ano | findstr :8501

# Check Streamlit version
streamlit --version

# Clear Streamlit cache
streamlit cache clear
```

### ESP32 Won't Connect

```bash
# Check WiFi credentials
# Check MQTT broker reachability
ping test.mosquitto.org

# Check Serial Monitor output
# Arduino IDE → Tools → Serial Monitor (115200 baud)
```

---

## 📞 SUPPORT

**Documentation:**
- API Docs: `docs/API_DOCUMENTATION.md`
- Architecture: `system.md`
- Hardware Guide: `docs/esp32_hardware_guide.md`

**Contact:**
- Email: support@iot-security.com
- GitHub: https://github.com/your-org/DoAnIoT

---

**Last Updated:** January 6, 2026  
**Version:** 1.0  
**Deployment Status:** Production Ready
