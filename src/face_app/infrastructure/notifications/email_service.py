"""Email notification service for alerts."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List


class EmailNotificationService:
    """Service to send email alerts."""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        recipient_emails: List[str],
        enabled: bool = True
    ):
        """
        Initialize email service.
        
        Args:
            smtp_server: SMTP server address (e.g., smtp.gmail.com)
            smtp_port: SMTP port (587 for TLS, 465 for SSL)
            sender_email: Email address to send from
            sender_password: Password or App Password
            recipient_emails: List of recipient email addresses
            enabled: Enable/disable email notifications
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_emails = recipient_emails
        self.enabled = enabled
    
    def send_stranger_alert(self, stranger_count: int, detection_time: datetime) -> bool:
        """
        Send stranger detection alert email.
        
        Args:
            stranger_count: Number of stranger detections
            detection_time: Time of detection
            
        Returns:
            True if email sent successfully
        """
        if not self.enabled:
            print("📧 Email notifications disabled")
            return False
        
        if not self.recipient_emails:
            print("⚠️  No recipient emails configured")
            return False
        
        # Create email content
        subject = f"🚨 CẢNH BÁO: Phát hiện {stranger_count} người lạ!"
        
        body = f"""
Hệ thống nhận diện khuôn mặt phát hiện hoạt động bất thường!

📊 Thông tin:
- Số lượng người lạ: {stranger_count} lần
- Thời gian: {detection_time.strftime('%Y-%m-%d %H:%M:%S')}
- Ngưỡng cảnh báo: 10 lần/phút

⚠️  Hành động khuyến nghị:
- Kiểm tra camera ngay
- Xác nhận người lạ
- Liên hệ bảo vệ nếu cần

---
Hệ thống Face Recognition Camera App
Được gửi tự động - Không reply email này
        """
        
        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = ', '.join(self.recipient_emails)
            message['Subject'] = subject
            
            message.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            print(f"📧 Đang gửi email tới {len(self.recipient_emails)} người nhận...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable TLS
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"✅ Đã gửi email cảnh báo thành công!")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi gửi email: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """Send a test email to verify configuration."""
        try:
            subject = "🔧 Test Email - Face Recognition System"
            body = f"""
Đây là email test từ hệ thống Face Recognition.

Nếu bạn nhận được email này, cấu hình email đã hoạt động!

Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            message = MIMEMultipart()
            message['From'] = self.sender_email
            message['To'] = ', '.join(self.recipient_emails)
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print("✅ Test email sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Test email failed: {e}")
            return False


# Example usage for Gmail:
# 1. Enable 2-Factor Authentication in Google Account
# 2. Generate App Password: https://myaccount.google.com/apppasswords
# 3. Use App Password instead of regular password
