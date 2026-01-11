# Cấu hình Email cho Cảnh Báo Người Lạ

## Windows PowerShell

Tạo file `.env` (hoặc set biến môi trường):

```powershell
# Gmail settings
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SENDER_EMAIL = "your_email@gmail.com"
$env:SENDER_PASSWORD = "your_app_password"  # NOT regular password!
$env:RECIPIENT_EMAILS = "recipient1@gmail.com,recipient2@gmail.com"
```

## Cách lấy App Password từ Gmail:

1. **Bật 2-Factor Authentication:**
   - Vào: https://myaccount.google.com/security
   - Tìm "2-Step Verification" → Bật lên

2. **Tạo App Password:**
   - Vào: https://myaccount.google.com/apppasswords
   - Chọn "Select app" → "Other (Custom name)"
   - Đặt tên: "Face Recognition App"
   - Click "Generate"
   - Copy mật khẩu 16 ký tự (không có khoảng trắng)

3. **Dùng App Password thay vì mật khẩu thường:**
   ```powershell
   $env:SENDER_PASSWORD = "abcd efgh ijkl mnop"  # App Password từ Gmail
   ```

## Chạy App:

```powershell
# Set environment variables
$env:SENDER_EMAIL = "your_email@gmail.com"
$env:SENDER_PASSWORD = "your_app_password"
$env:RECIPIENT_EMAILS = "family@gmail.com"

# Run app
python run.py
```

## Test Email:

```python
from face_app.infrastructure.notifications.email_service import EmailNotificationService
from datetime import datetime

service = EmailNotificationService(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    sender_email="your_email@gmail.com",
    sender_password="your_app_password",
    recipient_emails=["recipient@gmail.com"]
)

# Send test
service.send_test_email()

# Send alert
service.send_stranger_alert(12, datetime.now())
```

## Cấu hình trong settings.py:

Mặc định đọc từ biến môi trường, hoặc sửa trực tiếp:

```python
# src/face_app/config/settings.py
ENABLE_STRANGER_ALERTS = True
STRANGER_TIME_WINDOW = 60  # seconds
STRANGER_THRESHOLD = 10  # detections

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"
RECIPIENT_EMAILS = ["family@gmail.com"]
```

## Troubleshooting:

**Lỗi: "Username and Password not accepted"**
- Kiểm tra đã bật 2FA chưa
- Kiểm tra dùng App Password (không phải password thường)
- App Password không có khoảng trắng

**Lỗi: "SMTPAuthenticationError"**
- Gmail chặn "Less secure app access" → Phải dùng App Password
- Kiểm tra email/password đúng

**Không nhận email:**
- Kiểm tra Spam folder
- Kiểm tra RECIPIENT_EMAILS đúng format
- Test với send_test_email()
