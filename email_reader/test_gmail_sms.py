#!/usr/bin/env python3
"""
Simple test for Gmail SMS notifications

This uses your existing Gmail authentication - no passwords needed!
"""

import os
from services.gmail_service import GmailService


def test_gmail_sms_simple():
    """Test SMS via Gmail - super simple!"""
    
    # ✅ REPLACE THESE WITH YOUR ACTUAL DETAILS:
    phone_number = "1234567890"  # Your phone number (digits only)
    carrier = "tmobile"          # Your carrier: tmobile, att, verizon, etc.
    message = "Hello from your email reader system! 📱"
    
    print("📱 Testing Gmail SMS...")
    print(f"   Phone: {phone_number}")
    print(f"   Carrier: {carrier}")
    print(f"   Message: {message}")
    
    try:
        # Use your existing Gmail authentication
        gmail_service = GmailService()
        
        # Send SMS
        success = gmail_service.send_sms_notification(
            phone_number=phone_number,
            carrier=carrier,
            message=message
        )
        
        if success:
            print(f"✅ SUCCESS! SMS sent to {phone_number}@{get_carrier_gateway(carrier)}")
            print("   Check your phone for the message!")
        else:
            print("❌ Failed to send SMS")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Make sure you have:")
        print("   1. Run Gmail authentication: python3 authenticate_gmail.py")
        print("   2. Updated your phone number and carrier above")


def get_carrier_gateway(carrier):
    """Get the SMS gateway for a carrier"""
    gateways = {
        'att': 'txt.att.net',
        'verizon': 'vtext.com',
        'tmobile': 'tmomail.net',
        'sprint': 'messaging.sprintpcs.com',
        'boost': 'smsmyboostmobile.com',
        'cricket': 'sms.cricketwireless.net',
        'uscellular': 'email.uscc.net',
        'metropcs': 'mymetropcs.com'
    }
    return gateways.get(carrier.lower(), 'unknown')


def test_via_api():
    """Test via API endpoint"""
    print("\n🌐 You can also test via API:")
    print("   1. Start the server: docker-compose up")
    print("   2. Test with curl:")
    print('   curl -X POST "http://localhost:8000/notifications/sms-gmail" \\')
    print('     -d "phone_number=1234567890&carrier=tmobile&message=Test message"')
    print("   3. Or go to: http://localhost:8000/docs")


if __name__ == "__main__":
    print("🔔 GMAIL SMS TEST")
    print("=" * 40)
    print()
    print("✨ This uses your existing Gmail authentication!")
    print("✨ No passwords or app passwords needed!")
    print("✨ Just update your phone number and carrier above")
    print()
    
    test_gmail_sms_simple()
    test_via_api()
    
    print("\n📋 Supported carriers:")
    carriers = ['att', 'verizon', 'tmobile', 'sprint', 'boost', 'cricket', 'uscellular', 'metropcs']
    for carrier in carriers:
        print(f"   {carrier}: {get_carrier_gateway(carrier)}")
    
    print("\n🎯 Next steps:")
    print("   1. Update phone_number and carrier in this script")
    print("   2. Run: python test_gmail_sms.py")
    print("   3. Check your phone for the SMS!") 