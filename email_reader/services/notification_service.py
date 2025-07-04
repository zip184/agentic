#!/usr/bin/env python3
"""
Notification Service

Supports multiple notification methods:
- SMS via Twilio
- Push notifications via Pushbullet
- Push notifications via Pushover
- Discord webhooks
- Slack webhooks
- Email to SMS gateway
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class NotificationType(Enum):
    SMS_TWILIO = "sms_twilio"
    SMS_GMAIL = "sms_gmail"
    PUSHBULLET = "pushbullet"
    PUSHOVER = "pushover"
    DISCORD = "discord"
    SLACK = "slack"


@dataclass
class NotificationConfig:
    """Configuration for different notification services"""
    # Twilio SMS
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_from_number: Optional[str] = None
    twilio_to_number: Optional[str] = None
    
    # Gmail SMS (uses existing Gmail auth)
    gmail_sms_phone_number: Optional[str] = None
    gmail_sms_carrier: Optional[str] = None
    
    # Pushbullet
    pushbullet_api_key: Optional[str] = None
    
    # Pushover
    pushover_user_key: Optional[str] = None
    pushover_app_token: Optional[str] = None
    
    # Discord
    discord_webhook_url: Optional[str] = None
    
    # Slack
    slack_webhook_url: Optional[str] = None


class NotificationService:
    """Service for sending notifications via multiple channels"""
    
    # Common SMS gateways
    SMS_GATEWAYS = {
        'att': '@txt.att.net',
        'verizon': '@vtext.com',
        'tmobile': '@tmomail.net',
        'sprint': '@messaging.sprintpcs.com',
        'boost': '@smsmyboostmobile.com',
        'cricket': '@sms.cricketwireless.net',
        'uscellular': '@email.uscc.net',
        'metropcs': '@mymetropcs.com'
    }
    
    def __init__(self, config: Optional[NotificationConfig] = None, gmail_service=None):
        """Initialize notification service with configuration"""
        self.config = config or self._load_config_from_env()
        self.gmail_service = gmail_service
    
    def _load_config_from_env(self) -> NotificationConfig:
        """Load configuration from environment variables"""
        return NotificationConfig(
            # Twilio
            twilio_account_sid=os.getenv('TWILIO_ACCOUNT_SID'),
            twilio_auth_token=os.getenv('TWILIO_AUTH_TOKEN'),
            twilio_from_number=os.getenv('TWILIO_FROM_NUMBER'),
            twilio_to_number=os.getenv('TWILIO_TO_NUMBER'),
            
            # Gmail SMS
            gmail_sms_phone_number=os.getenv('GMAIL_SMS_PHONE_NUMBER'),
            gmail_sms_carrier=os.getenv('GMAIL_SMS_CARRIER'),
            
            # Pushbullet
            pushbullet_api_key=os.getenv('PUSHBULLET_API_KEY'),
            
            # Pushover
            pushover_user_key=os.getenv('PUSHOVER_USER_KEY'),
            pushover_app_token=os.getenv('PUSHOVER_APP_TOKEN'),
            
            # Discord
            discord_webhook_url=os.getenv('DISCORD_WEBHOOK_URL'),
            
            # Slack
            slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL')
        )
    
    def send_notification(self, message: str, title: str = "Notification", 
                         methods: List[NotificationType] = None) -> Dict[str, bool]:
        """
        Send notification via specified methods
        
        Args:
            message: The notification message
            title: The notification title
            methods: List of notification methods to use (if None, uses all available)
            
        Returns:
            Dictionary of method -> success status
        """
        if methods is None:
            methods = self._get_available_methods()
        
        results = {}
        
        for method in methods:
            try:
                if method == NotificationType.SMS_TWILIO:
                    results[method.value] = self._send_sms_twilio(message)
                elif method == NotificationType.SMS_GMAIL:
                    results[method.value] = self._send_sms_gmail(message)
                elif method == NotificationType.PUSHBULLET:
                    results[method.value] = self._send_pushbullet(title, message)
                elif method == NotificationType.PUSHOVER:
                    results[method.value] = self._send_pushover(title, message)
                elif method == NotificationType.DISCORD:
                    results[method.value] = self._send_discord(title, message)
                elif method == NotificationType.SLACK:
                    results[method.value] = self._send_slack(title, message)
                else:
                    results[method.value] = False
                    
            except Exception as e:
                print(f"Error sending notification via {method.value}: {e}")
                results[method.value] = False
        
        return results
    
    def _get_available_methods(self) -> List[NotificationType]:
        """Get list of available notification methods based on configuration"""
        methods = []
        
        if (self.config.twilio_account_sid and self.config.twilio_auth_token and 
            self.config.twilio_from_number and self.config.twilio_to_number):
            methods.append(NotificationType.SMS_TWILIO)
        
        if (self.gmail_service and self.config.gmail_sms_phone_number and 
            self.config.gmail_sms_carrier):
            methods.append(NotificationType.SMS_GMAIL)
        
        if self.config.pushbullet_api_key:
            methods.append(NotificationType.PUSHBULLET)
        
        if self.config.pushover_user_key and self.config.pushover_app_token:
            methods.append(NotificationType.PUSHOVER)
        
        if self.config.discord_webhook_url:
            methods.append(NotificationType.DISCORD)
        
        if self.config.slack_webhook_url:
            methods.append(NotificationType.SLACK)
        
        return methods
    
    def _send_sms_twilio(self, message: str) -> bool:
        """Send SMS via Twilio"""
        try:
            from twilio.rest import Client
            
            client = Client(self.config.twilio_account_sid, self.config.twilio_auth_token)
            
            message = client.messages.create(
                body=message,
                from_=self.config.twilio_from_number,
                to=self.config.twilio_to_number
            )
            
            return True
            
        except Exception as e:
            print(f"Twilio SMS error: {e}")
            return False
    
    def _send_sms_gmail(self, message: str) -> bool:
        """Send SMS via Gmail API using existing authentication"""
        try:
            if not self.gmail_service:
                print("Gmail service not available")
                return False
                
            return self.gmail_service.send_sms_notification(
                self.config.gmail_sms_phone_number,
                self.config.gmail_sms_carrier,
                message
            )
            
        except Exception as e:
            print(f"Gmail SMS error: {e}")
            return False
    
    def _send_pushbullet(self, title: str, message: str) -> bool:
        """Send push notification via Pushbullet"""
        try:
            url = "https://api.pushbullet.com/v2/pushes"
            headers = {
                "Access-Token": self.config.pushbullet_api_key,
                "Content-Type": "application/json"
            }
            data = {
                "type": "note",
                "title": title,
                "body": message
            }
            
            response = requests.post(url, headers=headers, json=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Pushbullet error: {e}")
            return False
    
    def _send_pushover(self, title: str, message: str) -> bool:
        """Send push notification via Pushover"""
        try:
            url = "https://api.pushover.net/1/messages.json"
            data = {
                "token": self.config.pushover_app_token,
                "user": self.config.pushover_user_key,
                "title": title,
                "message": message
            }
            
            response = requests.post(url, data=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Pushover error: {e}")
            return False
    
    def _send_discord(self, title: str, message: str) -> bool:
        """Send message to Discord webhook"""
        try:
            data = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": 5814783  # Blue color
                }]
            }
            
            response = requests.post(self.config.discord_webhook_url, json=data)
            return response.status_code == 204
            
        except Exception as e:
            print(f"Discord error: {e}")
            return False
    
    def _send_slack(self, title: str, message: str) -> bool:
        """Send message to Slack webhook"""
        try:
            data = {
                "text": f"*{title}*\n{message}"
            }
            
            response = requests.post(self.config.slack_webhook_url, json=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Slack error: {e}")
            return False
    

    
    def get_sms_gateway_address(self, phone_number: str, carrier: str) -> Optional[str]:
        """
        Get email-to-SMS gateway address for a phone number and carrier
        
        Args:
            phone_number: Phone number (digits only)
            carrier: Carrier name (att, verizon, tmobile, etc.)
            
        Returns:
            Email address for SMS gateway
        """
        if carrier.lower() in self.SMS_GATEWAYS:
            return f"{phone_number}{self.SMS_GATEWAYS[carrier.lower()]}"
        return None
    
    def test_notifications(self) -> Dict[str, bool]:
        """Test all configured notification methods"""
        return self.send_notification(
            "Test notification from your email reader system!",
            "Test Notification"
        )


# Convenience functions
def send_quick_notification(message: str, title: str = "Alert"):
    """Quick way to send a notification using environment variables"""
    service = NotificationService()
    return service.send_notification(message, title)


 