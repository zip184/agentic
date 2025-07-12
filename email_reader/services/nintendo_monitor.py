import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
from dataclasses import dataclass

from services.gmail_service import GmailService
from agents.memory_agent import MemoryAwareAgent
from memory.chroma_memory import ChromaMemoryManager
from services.notification_service import NotificationService, NotificationType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AlertConfig:
    """Configuration for different alert methods"""
    method: str  # 'console', 'webhook', 'email', 'file', 'pushover'
    target: str  # URL for webhook, email address, file path, etc.
    enabled: bool = True

class NintendoSwitch2Monitor:
    """
    Monitors Gmail for Nintendo Switch 2 related emails and sends alerts
    """
    
    def __init__(self, gmail_service: GmailService = None, memory_manager: ChromaMemoryManager = None):
        self.gmail_service = gmail_service or GmailService()
        self.memory_manager = memory_manager or ChromaMemoryManager()
        self.agent = MemoryAwareAgent(self.memory_manager)
        
        # Initialize notification service for Pushover alerts
        try:
            self.notification_service = NotificationService(gmail_service=self.gmail_service)
            logger.info("Notification service initialized for Nintendo monitor")
        except Exception as e:
            self.notification_service = None
            logger.warning(f"Notification service not available: {e}")
        
        # Nintendo-related sender patterns
        self.nintendo_senders = [
            "nintendo.com",
            "nintendo.co.jp", 
            "nintendo-europe.com",
            "mynintendo.com",
            "nintendo.net",
            "gmail.com"  # Temporary addition for testing
        ]
        
        # Switch 2 related keywords to look for
        self.switch2_keywords = [
            "switch 2",
            "nintendo switch 2", 
            "switch successor",
            "new nintendo switch",
            "next nintendo switch",
            "switch pro",
            "nintendo nx"
        ]
        
        # Purchase-related keywords
        self.purchase_keywords = [
            "pre-order",
            "preorder", 
            "available now",
            "purchase",
            "buy now",
            "order",
            "sale",
            "release",
            "launch"
        ]
        
        self.last_check = None
        self.alert_configs = []
        
        # Automatically add Pushover alert if configured
        self._add_pushover_alert_if_available()
        
    def _add_pushover_alert_if_available(self):
        """Automatically add Pushover alert if credentials are available"""
        if self.notification_service:
            available_methods = self.notification_service._get_available_methods()
            if NotificationType.PUSHOVER in available_methods:
                # Add Pushover alert config
                pushover_config = AlertConfig(
                    method="pushover",
                    target="",  # Not needed for Pushover
                    enabled=True
                )
                self.alert_configs.append(pushover_config)
                logger.info("🔔 Pushover notifications enabled for Nintendo monitoring")
            else:
                logger.info("Pushover not configured - missing PUSHOVER_USER_KEY or PUSHOVER_APP_TOKEN")
    
    def add_alert_config(self, config: AlertConfig):
        """Add an alert configuration"""
        self.alert_configs.append(config)
        logger.info(f"Added alert config: {config.method} -> {config.target}")
    
    async def monitor_emails(self, check_interval_minutes: int = 15):
        """
        Main monitoring loop - checks for Nintendo Switch 2 emails periodically
        
        Args:
            check_interval_minutes: How often to check for new emails
        """
        logger.info(f"Starting Nintendo Switch 2 email monitoring (checking every {check_interval_minutes} minutes)")
        
        while True:
            try:
                await self._check_for_switch2_emails()
                logger.info(f"Email check completed. Next check in {check_interval_minutes} minutes.")
                await asyncio.sleep(check_interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error during email check: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying on error
    
    async def _check_for_switch2_emails(self):
        """Check for new Nintendo Switch 2 related emails"""
        
        # Search for emails from Nintendo in the last 24 hours
        query_parts = []
        
        # Add Nintendo sender filters
        sender_queries = [f"from:{sender}" for sender in self.nintendo_senders]
        query_parts.append(f"({' OR '.join(sender_queries)})")
        
        # Only check recent emails (last 30 days to account for date issues)
        last_month = datetime.now() - timedelta(days=30)
        query_parts.append(f"after:{last_month.strftime('%Y/%m/%d')}")
        
        gmail_query = " ".join(query_parts)
        
        logger.info(f"Searching Gmail with query: {gmail_query}")
        
        try:
            # Get emails from Nintendo
            nintendo_emails = self.gmail_service.get_messages(
                query=gmail_query,
                max_results=50
            )
            
            if not nintendo_emails:
                logger.info("No recent Nintendo emails found")
                return
            
            logger.info(f"Found {len(nintendo_emails)} recent Nintendo emails to analyze")
            
            # Analyze each email for Switch 2 content
            for email in nintendo_emails:
                await self._analyze_email_for_switch2(email)
                
        except Exception as e:
            logger.error(f"Error checking emails: {e}")
            # Send failure notification using existing notification system
            await self._send_failure_notification(str(e))
    
    async def _analyze_email_for_switch2(self, email: Dict[str, Any]):
        """Analyze an individual email for Switch 2 content"""
        
        email_id = email.get('id', 'unknown')
        subject = email.get('subject', '')
        body = email.get('body_clean', '')
        sender = email.get('from', '')
        
        logger.info(f"Processing email ID: {email_id}, Subject: {subject}")
        
        # Check if we've already processed this email
        memory_query = f"Processed Nintendo email {email_id}"
        existing_memories = self.memory_manager.search_memories(memory_query, limit=1)
        
        if existing_memories:
            logger.info(f"Email {email_id} already processed, skipping duplicate alert")
            return
        
        # Combine subject and body for analysis
        email_content = f"{subject} {body}".lower()
        
        # Check for Switch 2 keywords
        switch2_matches = [kw for kw in self.switch2_keywords if kw.lower() in email_content]
        purchase_matches = [kw for kw in self.purchase_keywords if kw.lower() in email_content]
        
        if switch2_matches and purchase_matches:
            # This looks like a Switch 2 purchase email!
            await self._handle_switch2_email_found(email, switch2_matches, purchase_matches)
        
        elif switch2_matches:
            # Switch 2 mentioned but not purchase-related
            logger.info(f"Switch 2 mentioned in email from {sender}: {subject}")
            await self._handle_switch2_mention(email, switch2_matches)
        
        # Store that we've processed this email
        self.agent.add_observation(
            observation=f"Processed Nintendo email {email_id}: {subject}",
            importance_score=0.3,
            metadata={
                "email_id": email_id,
                "sender": sender,
                "switch2_matches": ", ".join(switch2_matches),
                "purchase_matches": ", ".join(purchase_matches)
            }
        )
    
    async def _handle_switch2_email_found(self, email: Dict[str, Any], 
                                        switch2_matches: List[str], 
                                        purchase_matches: List[str]):
        """Handle when we find a potential Switch 2 purchase email"""
        
        email_id = email.get('id', 'unknown')
        subject = email.get('subject', '')
        sender = email.get('from', '')
        date = email.get('date', '')
        
        # Use AI agent to analyze the email importance
        analysis_goal = f"Analyze this Nintendo email to determine if it's about Switch 2 availability"
        email_context = f"""
        Email from: {sender}
        Subject: {subject}
        Date: {date}
        Switch 2 keywords found: {', '.join(switch2_matches)}
        Purchase keywords found: {', '.join(purchase_matches)}
        Body preview: {email.get('body_clean', '')[:500]}...
        """
        
        ai_analysis = self.agent.run_agent(goal=analysis_goal, current_context=email_context)
        
        alert_data = {
            "email_id": email_id,
            "subject": subject,
            "sender": sender,
            "date": date,
            "switch2_keywords": switch2_matches,
            "purchase_keywords": purchase_matches,
            "ai_analysis": ai_analysis,
            "urgency": "HIGH",
            "message": f"🎮 NINTENDO SWITCH 2 EMAIL DETECTED! 🚨\n\nSubject: {subject}\nFrom: {sender}\nDate: {date}"
        }
        
        # Send alerts through all configured methods
        for config in self.alert_configs:
            if config.enabled:
                await self._send_alert(config, alert_data)
        
        # Store as high-importance memory
        self.agent.add_learning(
            learning=f"CRITICAL: Nintendo Switch 2 purchase email detected from {sender}: {subject}",
            importance_score=1.0,
            metadata=alert_data
        )
        
        logger.critical(f"🎮 SWITCH 2 EMAIL FOUND! Subject: {subject}")
    
    async def _handle_switch2_mention(self, email: Dict[str, Any], switch2_matches: List[str]):
        """Handle when Switch 2 is mentioned but not purchase-related"""
        
        subject = email.get('subject', '')
        sender = email.get('from', '')
        
        # Lower priority alert
        alert_data = {
            "email_id": email.get('id', ''),
            "subject": subject,
            "sender": sender,
            "date": email.get('date', ''),
            "switch2_keywords": switch2_matches,
            "urgency": "MEDIUM",
            "message": f"📧 Nintendo Switch 2 mentioned in email\n\nSubject: {subject}\nFrom: {sender}"
        }
        
        # Send lower priority alerts (including Pushover for mentions)
        for config in self.alert_configs:
            if config.enabled and config.method in ['console', 'file', 'pushover']:
                await self._send_alert(config, alert_data)
        
        logger.info(f"📧 Switch 2 mentioned: {subject}")
    
    async def _send_alert(self, config: AlertConfig, alert_data: Dict[str, Any]):
        """Send an alert using the specified configuration"""
        
        try:
            if config.method == 'console':
                await self._send_console_alert(alert_data)
            elif config.method == 'file':
                await self._send_file_alert(config.target, alert_data)
            elif config.method == 'webhook':
                await self._send_webhook_alert(config.target, alert_data)
            elif config.method == 'email':
                await self._send_email_alert(config.target, alert_data)
            elif config.method == 'pushover':
                await self._send_pushover_alert(alert_data)
            else:
                logger.warning(f"Unknown alert method: {config.method}")
                
        except Exception as e:
            logger.error(f"Failed to send {config.method} alert: {e}")
    
    async def _send_console_alert(self, alert_data: Dict[str, Any]):
        """Send alert to console"""
        print("\n" + "="*60)
        print(alert_data['message'])
        print("="*60)
        if alert_data.get('ai_analysis'):
            print(f"AI Analysis: {alert_data['ai_analysis']}")
        print()
    
    async def _send_file_alert(self, file_path: str, alert_data: Dict[str, Any]):
        """Send alert to file"""
        timestamp = datetime.now().isoformat()
        alert_entry = f"\n[{timestamp}] {alert_data['urgency']}: {alert_data['message']}\n"
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(alert_entry)
    
    async def _send_webhook_alert(self, webhook_url: str, alert_data: Dict[str, Any]):
        """Send alert via webhook"""
        payload = {
            "timestamp": datetime.now().isoformat(),
            "alert_type": "nintendo_switch2",
            "urgency": alert_data['urgency'],
            "data": alert_data
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Webhook alert sent successfully to {webhook_url}")
    
    async def _send_email_alert(self, email_address: str, alert_data: Dict[str, Any]):
        """Send alert via email (would need SMTP configuration)"""
        # This would require SMTP setup - placeholder for now
        logger.info(f"Email alert would be sent to {email_address}: {alert_data['message']}")
    
    async def _send_pushover_alert(self, alert_data: Dict[str, Any]):
        """Send alert via Pushover"""
        if not self.notification_service:
            logger.warning("Notification service not available for Pushover alert")
            return
        
        try:
            # Create title and message for Pushover
            title = f"Nintendo Switch 2 Alert - {alert_data['urgency']}"
            message = alert_data['message']
            
            # Add AI analysis if available
            if alert_data.get('ai_analysis'):
                message += f"\n\nAI Analysis: {alert_data['ai_analysis']}"
            
            # Send via Pushover
            result = self.notification_service.send_notification(
                message=message,
                title=title,
                methods=[NotificationType.PUSHOVER]
            )
            
            if result.get('pushover', False):
                logger.info("✅ Pushover alert sent successfully!")
            else:
                logger.error("❌ Failed to send Pushover alert")
                
        except Exception as e:
            logger.error(f"Error sending Pushover alert: {e}")
    
    async def _send_failure_notification(self, error_message: str):
        """Send notification when monitoring fails"""
        if not self.notification_service:
            logger.warning("Notification service not available for failure alert")
            return
        
        try:
            title = "🚨 Nintendo Monitor Failed"
            message = f"Nintendo Switch 2 monitoring encountered an error:\n\n{error_message}\n\nPlease check the service and logs."
            
            # Send via all available notification methods
            result = self.notification_service.send_notification(
                message=message,
                title=title
            )
            
            success_count = sum(1 for success in result.values() if success)
            if success_count > 0:
                logger.info(f"✅ Failure notification sent via {success_count} method(s)")
            else:
                logger.error("❌ Failed to send failure notification")
                
        except Exception as e:
            logger.error(f"Error sending failure notification: {e}")
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get statistics about the monitoring"""
        # Check if Pushover is available
        pushover_available = False
        if self.notification_service:
            available_methods = self.notification_service._get_available_methods()
            pushover_available = NotificationType.PUSHOVER in available_methods
        
        return {
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "nintendo_senders": self.nintendo_senders,
            "switch2_keywords": self.switch2_keywords,
            "purchase_keywords": self.purchase_keywords,
            "alert_configs": len(self.alert_configs),
            "pushover_available": pushover_available,
            "memory_stats": self.agent.get_memory_stats()
        } 