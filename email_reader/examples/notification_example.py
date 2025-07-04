#!/usr/bin/env python3
"""
Notification Service Examples

This file demonstrates how to use the notification service
with different notification methods.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.notification_service import NotificationService, NotificationType, send_sms_via_email, send_quick_notification


def example_email_to_sms():
    """Example: Send SMS via email-to-SMS gateway (Free!)"""
    print("📱 Email to SMS Example")
    print("=" * 40)
    
    # This is the easiest method - no additional services required
    # Just use your existing email account
    
    phone_number = "1234567890"  # Replace with your phone number
    carrier = "att"  # Replace with your carrier (att, verizon, tmobile, etc.)
    message = "Hello from your email reader system!"
    
    # Use your Gmail credentials (use App Password if 2FA is enabled)
    email_username = "your-email@gmail.com"
    email_password = "your-app-password"
    
    success = send_sms_via_email(
        phone_number=phone_number,
        carrier=carrier,
        message=message,
        email_username=email_username,
        email_password=email_password
    )
    
    if success:
        print("✅ SMS sent successfully!")
    else:
        print("❌ Failed to send SMS")
    
    print("\n💡 Tip: For Gmail, use an App Password instead of your regular password")
    print("   Go to: Google Account > Security > App passwords")


def example_pushbullet():
    """Example: Send push notification via Pushbullet (Free tier available)"""
    print("\n📲 Pushbullet Example")
    print("=" * 40)
    
    # Set up your Pushbullet API key
    os.environ['PUSHBULLET_API_KEY'] = 'your-pushbullet-api-key'
    
    service = NotificationService()
    result = service.send_notification(
        "New important email received!",
        "Email Alert",
        [NotificationType.PUSHBULLET]
    )
    
    print(f"Result: {result}")
    print("\n💡 Get your API key from: https://www.pushbullet.com/#settings")


def example_discord():
    """Example: Send notification to Discord webhook (Free!)"""
    print("\n💬 Discord Example")
    print("=" * 40)
    
    # Set up your Discord webhook URL
    os.environ['DISCORD_WEBHOOK_URL'] = 'https://discord.com/api/webhooks/your-webhook-url'
    
    service = NotificationService()
    result = service.send_notification(
        "System alert: New email from important sender",
        "Email Monitor",
        [NotificationType.DISCORD]
    )
    
    print(f"Result: {result}")
    print("\n💡 Create webhook: Discord Server > Settings > Integrations > Webhooks")


def example_twilio_sms():
    """Example: Send SMS via Twilio (Paid service)"""
    print("\n📞 Twilio SMS Example")
    print("=" * 40)
    
    # Set up your Twilio credentials
    os.environ['TWILIO_ACCOUNT_SID'] = 'your-twilio-account-sid'
    os.environ['TWILIO_AUTH_TOKEN'] = 'your-twilio-auth-token'
    os.environ['TWILIO_FROM_NUMBER'] = '+1234567890'  # Your Twilio phone number
    os.environ['TWILIO_TO_NUMBER'] = '+0987654321'    # Your personal phone number
    
    service = NotificationService()
    result = service.send_notification(
        "Alert: Critical email received",
        "Email System",
        [NotificationType.SMS_TWILIO]
    )
    
    print(f"Result: {result}")
    print("\n💡 Get credentials from: https://console.twilio.com/")


def example_multiple_methods():
    """Example: Send notification via multiple methods"""
    print("\n🔄 Multiple Methods Example")
    print("=" * 40)
    
    # Set up multiple notification methods
    os.environ['PUSHBULLET_API_KEY'] = 'your-pushbullet-api-key'
    os.environ['DISCORD_WEBHOOK_URL'] = 'https://discord.com/api/webhooks/your-webhook-url'
    
    service = NotificationService()
    
    # This will send via all available methods
    result = service.send_notification(
        "Multi-channel alert: System status update",
        "System Monitor"
    )
    
    print(f"Results: {result}")
    
    # Or specify particular methods
    result = service.send_notification(
        "Targeted notification",
        "Email Alert",
        [NotificationType.PUSHBULLET, NotificationType.DISCORD]
    )
    
    print(f"Targeted results: {result}")


def example_quick_notification():
    """Example: Quick notification using environment variables"""
    print("\n⚡ Quick Notification Example")
    print("=" * 40)
    
    # Set up any notification method via environment variables
    os.environ['PUSHBULLET_API_KEY'] = 'your-pushbullet-api-key'
    
    # Send a quick notification
    result = send_quick_notification("Quick alert message!", "System Alert")
    
    print(f"Quick notification result: {result}")


def example_test_setup():
    """Example: Test your notification setup"""
    print("\n🧪 Test Setup Example")
    print("=" * 40)
    
    # Set up your preferred notification method
    os.environ['PUSHBULLET_API_KEY'] = 'your-pushbullet-api-key'
    
    service = NotificationService()
    
    # Test all configured methods
    results = service.test_notifications()
    
    print("Test results:")
    for method, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {method}")


def setup_email_to_sms_guide():
    """Guide for setting up email-to-SMS (the easiest method)"""
    print("\n📧➡️📱 Email-to-SMS Setup Guide")
    print("=" * 50)
    
    print("This is the EASIEST way to get SMS notifications:")
    print()
    print("1. Find your carrier's SMS gateway:")
    
    service = NotificationService()
    print("   Supported carriers:")
    for carrier, gateway in service.SMS_GATEWAYS.items():
        print(f"     {carrier}: [your-number]{gateway}")
    
    print()
    print("2. Example: If your phone number is 1234567890 and you have AT&T:")
    print("   SMS address: 1234567890@txt.att.net")
    
    print()
    print("3. Set up environment variables:")
    print("   EMAIL_USERNAME=your-email@gmail.com")
    print("   EMAIL_PASSWORD=your-app-password")
    print("   EMAIL_TO_SMS_ADDRESS=1234567890@txt.att.net")
    
    print()
    print("4. For Gmail, create an App Password:")
    print("   - Go to Google Account > Security > App passwords")
    print("   - Generate a new app password")
    print("   - Use that password, not your regular Gmail password")
    
    print()
    print("5. Test it:")
    print("   python examples/notification_example.py")


if __name__ == "__main__":
    print("🔔 Notification Service Examples")
    print("=" * 50)
    
    # Show setup guide first
    setup_email_to_sms_guide()
    
    print("\n\n💡 Uncomment the examples you want to try:")
    print("   (Make sure to add your actual credentials first!)")
    
    # Uncomment and modify these examples with your actual credentials:
    
    # example_email_to_sms()
    # example_pushbullet()
    # example_discord()
    # example_twilio_sms()
    # example_multiple_methods()
    # example_quick_notification()
    # example_test_setup() 