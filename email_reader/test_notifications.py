#!/usr/bin/env python3
"""
Test script for the notification system

This script shows how to test different notification methods.
"""

import os
import sys
from services.notification_service import NotificationService, NotificationType, send_quick_notification


def test_gmail_sms():
    """Test SMS via existing Gmail authentication (easiest method!)"""
    print("📱 Testing Gmail SMS (No passwords needed!)...")
    
    # Replace these with your actual details
    phone_number = "1234567890"  # Your phone number (digits only)
    carrier = "tmobile"  # Your carrier (att, verizon, tmobile, etc.)
    message = "Test message from your email reader system!"
    
    # Set up environment variables (in real use, put these in .env file)
    os.environ['GMAIL_SMS_PHONE_NUMBER'] = phone_number
    os.environ['GMAIL_SMS_CARRIER'] = carrier
    
    try:
        from services.gmail_service import GmailService
        
        # Use your existing Gmail authentication
        gmail_service = GmailService()
        service = NotificationService(gmail_service=gmail_service)
        
        available_methods = service._get_available_methods()
        print(f"Available methods: {[m.value for m in available_methods]}")
        
        if available_methods:
            result = service.send_notification(
                message,
                "Test SMS",
                [NotificationType.SMS_GMAIL]
            )
            print(f"Results: {result}")
        else:
            print("No notification methods configured")
            
    except Exception as e:
        print(f"❌ Error: {e}")





def test_environment_variables():
    """Test using environment variables"""
    print("\n🌍 Testing Environment Variables...")
    
    # Set up environment variables (in real use, put these in .env file)
    os.environ['EMAIL_USERNAME'] = 'your-email@gmail.com'
    os.environ['EMAIL_PASSWORD'] = 'your-app-password'
    os.environ['EMAIL_TO_SMS_ADDRESS'] = '1234567890@txt.att.net'
    
    try:
        service = NotificationService()
        available_methods = service._get_available_methods()
        
        print(f"Available methods: {[m.value for m in available_methods]}")
        
        if available_methods:
            result = service.send_notification(
                "Test notification from environment variables!",
                "System Test"
            )
            print(f"Results: {result}")
        else:
            print("No notification methods configured")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_quick_notification():
    """Test quick notification"""
    print("\n⚡ Testing Quick Notification...")
    
    # Set up at least one method
    os.environ['EMAIL_USERNAME'] = 'your-email@gmail.com'
    os.environ['EMAIL_PASSWORD'] = 'your-app-password'
    os.environ['EMAIL_TO_SMS_ADDRESS'] = '1234567890@txt.att.net'
    
    try:
        result = send_quick_notification("Quick test message!", "Quick Test")
        print(f"Quick notification result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")


def show_setup_guide():
    """Show setup guide"""
    print("🔧 NOTIFICATION SETUP GUIDE")
    print("=" * 50)
    
    print("\n1. GMAIL SMS (Easiest - Uses your existing Gmail auth!)")
    print("   - No passwords needed - uses your existing Gmail authentication")
    print("   - Just set up environment variables:")
    print("     GMAIL_SMS_PHONE_NUMBER=1234567890")
    print("     GMAIL_SMS_CARRIER=tmobile")
    
    print("\n2. PUSHBULLET (Free tier available)")
    print("   - Get API key from: https://www.pushbullet.com/#settings")
    print("   - Environment variable: PUSHBULLET_API_KEY=your-key")
    
    print("\n3. DISCORD (Free!)")
    print("   - Create webhook in Discord server")
    print("   - Environment variable: DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...")
    
    print("\n4. TWILIO SMS (Paid service)")
    print("   - Sign up at: https://console.twilio.com/")
    print("   - Environment variables:")
    print("     TWILIO_ACCOUNT_SID=your-sid")
    print("     TWILIO_AUTH_TOKEN=your-token")
    print("     TWILIO_FROM_NUMBER=+1234567890")
    print("     TWILIO_TO_NUMBER=+0987654321")
    
    print("\n5. PUSHOVER (One-time fee)")
    print("   - Get credentials from: https://pushover.net/")
    print("   - Environment variables:")
    print("     PUSHOVER_USER_KEY=your-user-key")
    print("     PUSHOVER_APP_TOKEN=your-app-token")
    

    
    print("\n🏃‍♂️ To test:")
    print("   1. Update the credentials in this script")
    print("   2. Run: python test_notifications.py")
    print("   3. Or use the API: http://localhost:8000/docs#/notifications")


if __name__ == "__main__":
    print("🔔 NOTIFICATION SYSTEM TEST")
    print("=" * 50)
    
    show_setup_guide()
    
    print("\n\n💡 UPDATE THE PHONE NUMBER AND CARRIER AND UNCOMMENT TO TEST:")
    print("   (Replace '1234567890' with your phone number and 'tmobile' with your carrier)")
    
    # Uncomment these lines and add your actual phone number/carrier to test:
    # test_gmail_sms()  # <- Try this first! No passwords needed!
    # test_environment_variables()
    # test_quick_notification()
    
    print("\n🌐 You can also test via the web API:")
    print("   1. Start the server: docker-compose up")
    print("   2. Go to: http://localhost:8000/docs")
    print("   3. Look for the 'Notification' endpoints")
    print("   4. Try the GET /notifications/status endpoint first") 