"""
Alert Service - Gửi cảnh báo qua Email và Telegram
Hỗ trợ multiple channels, configurable thresholds
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime
import requests
from ..core.models import MotionEvent, PredictionResult, AlertLevel
from ..infrastructure.config import AlertConfig
import logging

logger = logging.getLogger(__name__)


class AlertService:
    """Service gửi cảnh báo qua nhiều kênh (Email, Telegram, Console)"""
    
    def __init__(self, config: Optional[AlertConfig] = None):
        self.config = config or AlertConfig()
        self.enabled_channels = self._init_channels()
        logger.info(f"Alert Service initialized. Enabled channels: {self.enabled_channels}")
    
    def _init_channels(self) -> List[str]:
        """Kiểm tra các kênh nào được kích hoạt"""
        channels = []
        
        # Always enable console alerts
        channels.append("console")
        
        # Check email configuration
        if self.config.email_enabled and self.config.smtp_host:
            channels.append("email")
            logger.info("Email alerts enabled")
        
        # Check Telegram configuration
        if self.config.telegram_enabled and self.config.telegram_bot_token:
            channels.append("telegram")
            logger.info("Telegram alerts enabled")
        
        return channels
    
    def send_alert(
        self, 
        event: MotionEvent, 
        prediction: PredictionResult,
        force: bool = False
    ) -> bool:
        """
        Gửi cảnh báo nếu đạt ngưỡng
        
        Args:
            event: Motion event
            prediction: AI prediction result
            force: Bắt buộc gửi bất kể ngưỡng
        
        Returns:
            True nếu alert được gửi thành công
        """
        # Check if alert should be sent
        if not force and not self._should_alert(prediction):
            logger.debug(f"Alert threshold not met. Alert level: {prediction.alert_level}")
            return False
        
        # Prepare alert message
        message = self._format_alert_message(event, prediction)
        subject = self._format_alert_subject(prediction)
        
        success = True
        
        # Send to all enabled channels
        if "console" in self.enabled_channels:
            self._send_console_alert(subject, message)
        
        if "email" in self.enabled_channels:
            success &= self._send_email_alert(subject, message)
        
        if "telegram" in self.enabled_channels:
            success &= self._send_telegram_alert(message)
        
        return success
    
    def _should_alert(self, prediction: PredictionResult) -> bool:
        """Kiểm tra xem có nên gửi alert không"""
        # Always alert for CRITICAL
        if prediction.alert_level == AlertLevel.CRITICAL:
            return True
        
        # Alert for WARNING if enabled
        if prediction.alert_level == AlertLevel.WARNING and self.config.alert_on_warning:
            return True
        
        # Check confidence threshold
        if prediction.confidence >= self.config.confidence_threshold:
            return True
        
        return False
    
    def _format_alert_subject(self, prediction: PredictionResult) -> str:
        """Tạo subject cho alert"""
        emoji_map = {
            AlertLevel.CRITICAL: "🚨",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.SAFE: "✅"
        }
        
        emoji = emoji_map.get(prediction.alert_level, "ℹ️")
        level = prediction.alert_level.value.upper()
        
        return f"{emoji} IoT Security Alert - {level}"
    
    def _format_alert_message(self, event: MotionEvent, prediction: PredictionResult) -> str:
        """Tạo nội dung alert message"""
        # Format timestamp
        timestamp_str = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # Alert level styling
        level_icon = {
            AlertLevel.CRITICAL: "🔴",
            AlertLevel.WARNING: "🟡",
            AlertLevel.SAFE: "🟢"
        }[prediction.alert_level]
        
        # Prediction label styling
        pred_icon = "⚠️" if prediction.prediction_label.value == "suspicious" else "✅"
        
        message = f"""
🔒 IoT SECURITY MONITORING SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{level_icon} ALERT LEVEL: {prediction.alert_level.value.upper()}
⏰ Timestamp: {timestamp_str}
📍 Location: {event.location}
🆔 Sensor ID: {event.sensor_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 DETECTION DETAILS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 Motion Detected: {"YES 🔴" if event.motion.value == 1 else "NO 🟢"}
{pred_icon} AI Prediction: {prediction.prediction_label.value.upper()}
📈 Confidence: {prediction.confidence:.1%}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 AI ANALYSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hour: {prediction.features.get('hour', 'N/A')}
Night Time: {"Yes" if prediction.features.get('is_night', 0) else "No"}
Frequency (5min): {prediction.features.get('frequency_5min', 0)}
Duration: {prediction.features.get('duration', 0)} events

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Add recommendation
        if prediction.alert_level == AlertLevel.CRITICAL:
            message += """
⚠️ RECOMMENDED ACTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Immediate investigation required
📹 Check surveillance cameras
🚨 Notify security personnel
"""
        elif prediction.alert_level == AlertLevel.WARNING:
            message += """
ℹ️ RECOMMENDED ACTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👀 Monitor for additional activity
📊 Review activity patterns
"""
        
        message += f"\n🌐 Dashboard: http://localhost:8501\n"
        message += f"📧 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return message
    
    def _send_console_alert(self, subject: str, message: str):
        """Hiển thị alert trên console"""
        print("\n" + "="*60)
        print(subject)
        print("="*60)
        print(message)
        print("="*60 + "\n")
        logger.info(f"Console alert sent: {subject}")
    
    def _send_email_alert(self, subject: str, message: str) -> bool:
        """Gửi email alert qua SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.smtp_from
            msg['To'] = ', '.join(self.config.alert_recipients)
            msg['Subject'] = subject
            
            # Plain text version
            text_part = MIMEText(message, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # HTML version (prettier)
            html_message = self._format_html_message(message, subject)
            html_part = MIMEText(html_message, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.smtp_use_tls:
                    server.starttls()
                
                if self.config.smtp_username and self.config.smtp_password:
                    server.login(self.config.smtp_username, self.config.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {len(self.config.alert_recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def _send_telegram_alert(self, message: str) -> bool:
        """Gửi alert qua Telegram Bot API"""
        try:
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
            
            for chat_id in self.config.telegram_chat_ids:
                payload = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'HTML'  # Support HTML formatting
                }
                
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"Telegram alert sent to chat_id: {chat_id}")
                else:
                    logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    def _format_html_message(self, plain_text: str, subject: str) -> str:
        """Chuyển plain text thành HTML đẹp hơn"""
        # Simple HTML template
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ background-color: white; border-radius: 10px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                .content {{ line-height: 1.8; color: #333; }}
                .footer {{ margin-top: 20px; padding-top: 20px; border-top: 2px solid #eee; font-size: 12px; color: #999; text-align: center; }}
                pre {{ background-color: #f8f8f8; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{subject}</h2>
                </div>
                <div class="content">
                    <pre>{plain_text}</pre>
                </div>
                <div class="footer">
                    <p>IoT Security Monitoring System</p>
                    <p>Automated Alert - Do Not Reply</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def test_connection(self) -> dict:
        """Test tất cả các kênh alert"""
        results = {}
        
        # Test console (always works)
        results['console'] = True
        
        # Test email
        if "email" in self.enabled_channels:
            try:
                with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port, timeout=5) as server:
                    if self.config.smtp_use_tls:
                        server.starttls()
                    if self.config.smtp_username and self.config.smtp_password:
                        server.login(self.config.smtp_username, self.config.smtp_password)
                results['email'] = True
                logger.info("Email connection test: SUCCESS")
            except Exception as e:
                results['email'] = False
                logger.error(f"Email connection test: FAILED - {e}")
        
        # Test Telegram
        if "telegram" in self.enabled_channels:
            try:
                url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/getMe"
                response = requests.get(url, timeout=5)
                results['telegram'] = response.status_code == 200
                logger.info(f"Telegram connection test: {'SUCCESS' if results['telegram'] else 'FAILED'}")
            except Exception as e:
                results['telegram'] = False
                logger.error(f"Telegram connection test: FAILED - {e}")
        
        return results


# Test script
if __name__ == "__main__":
    from datetime import datetime
    from ..core.models import MotionEvent, MotionStatus, PredictionResult, PredictionLabel, AlertLevel
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create test event
    event = MotionEvent(
        timestamp=datetime.now(),
        motion=MotionStatus.MOTION_DETECTED,
        sensor_id="PIR_TEST",
        location="Test Area"
    )
    
    # Create test prediction (CRITICAL alert)
    prediction = PredictionResult(
        timestamp=datetime.now(),
        motion_event=event,
        prediction_label=PredictionLabel.SUSPICIOUS,
        confidence=0.95,
        alert_level=AlertLevel.CRITICAL,
        features={'hour': 2, 'is_night': 1, 'frequency_5min': 5, 'duration': 3}
    )
    
    # Initialize alert service (console only by default)
    alert_service = AlertService()
    
    # Test connection
    print("\n🔍 Testing Alert Channels...")
    test_results = alert_service.test_connection()
    for channel, status in test_results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {channel.upper()}: {'Connected' if status else 'Failed'}")
    
    # Send test alert
    print("\n📤 Sending Test Alert...")
    success = alert_service.send_alert(event, prediction, force=True)
    
    if success:
        print("\n✅ Test alert sent successfully!")
    else:
        print("\n❌ Failed to send test alert")
