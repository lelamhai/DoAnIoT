"""Test email service."""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from face_app.infrastructure.notifications.email_service import EmailNotificationService
from face_app.config import settings
from datetime import datetime

print("=" * 60)
print("📧 Testing Email Service")
print("=" * 60)

print(f"\n📋 Configuration:")
print(f"   SMTP Server: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
print(f"   Sender: {settings.SENDER_EMAIL}")
print(f"   Password: {'*' * len(settings.SENDER_PASSWORD) if settings.SENDER_PASSWORD else '(empty)'}")
print(f"   Recipients: {settings.RECIPIENT_EMAILS}")

# Create service
service = EmailNotificationService(
    smtp_server=settings.SMTP_SERVER,
    smtp_port=settings.SMTP_PORT,
    sender_email=settings.SENDER_EMAIL,
    sender_password=settings.SENDER_PASSWORD,
    recipient_emails=settings.RECIPIENT_EMAILS,
    enabled=True
)

print("\n" + "=" * 60)
print("📨 Sending test email...")
print("=" * 60)

success = service.send_test_email()

if success:
    print("\n✅ Test email sent successfully!")
    print("📬 Check your inbox (and Spam folder):")
    for email in settings.RECIPIENT_EMAILS:
        print(f"   - {email}")
else:
    print("\n❌ Failed to send test email")
    print("\n💡 Common issues:")
    print("   1. Wrong password - Use App Password, not regular password!")
    print("   2. 2FA not enabled on Gmail")
    print("   3. Less secure apps blocked")
    print("\n🔧 To fix:")
    print("   1. Go to: https://myaccount.google.com/security")
    print("   2. Enable 2-Factor Authentication")
    print("   3. Go to: https://myaccount.google.com/apppasswords")
    print("   4. Generate App Password")
    print("   5. Update SENDER_PASSWORD in settings.py")

print("\n" + "=" * 60)
