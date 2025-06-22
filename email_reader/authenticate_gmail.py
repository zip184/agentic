#!/usr/bin/env python3
"""
Gmail Authentication Script

Run this script on your local machine (not in Docker) to authenticate with Gmail.
This will create a token.pickle file that can be used by the Docker container.

Usage:
    python3 authenticate_gmail.py
"""

import os
import sys

def main():
    print("🔐 Gmail Authentication Setup")
    print("="*50)
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ ERROR: credentials.json not found!")
        print("\n📋 Please ensure you have:")
        print("1. Downloaded credentials from Google Cloud Console")
        print("2. Renamed the file to 'credentials.json'")
        print("3. Placed it in this directory")
        sys.exit(1)
    
    try:
        # Install required packages if not available
        try:
            from services.gmail_service import authenticate_gmail
        except ImportError:
            print("📦 Installing required packages...")
            os.system("pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            from services.gmail_service import authenticate_gmail
        
        # Authenticate
        print("🚀 Starting Gmail authentication...")
        authenticate_gmail()
        
        print("\n✅ SUCCESS!")
        print("📁 The token.pickle file has been created.")
        print("🐳 You can now rebuild your Docker container:")
        print("   docker-compose down && docker-compose up --build -d")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\n🆘 If you see browser-related errors, try:")
        print("1. Make sure you're running this on your local machine (not in Docker)")
        print("2. Ensure you have a GUI/browser available")
        print("3. Check your internet connection")

if __name__ == "__main__":
    main() 