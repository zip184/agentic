import os
import json
import base64
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.utils import parsedate_tz, mktime_tz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email_reply_parser import EmailReplyParser

class GmailService:
    """Gmail API service for reading and managing emails"""
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
        """
        Initialize Gmail service
        
        Args:
            credentials_file: Path to Gmail API credentials file
            token_file: Path to store authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Check if token file exists
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"Warning: Could not load token file {self.token_file}: {e}")
                print("Removing invalid token file and re-authenticating...")
                os.remove(self.token_file)
                creds = None
        
        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("Attempting to refresh expired token...")
                    creds.refresh(Request())
                    print("✅ Token refreshed successfully!")
                except Exception as e:
                    print(f"⚠️  Token refresh failed: {e}")
                    print("Removing invalid token file and re-authenticating...")
                    # Remove the invalid token file
                    if os.path.exists(self.token_file):
                        os.remove(self.token_file)
                    creds = None
            
            # If we still don't have valid credentials, start fresh authentication
            if not creds or not creds.valid:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Gmail credentials file not found: {self.credentials_file}. "
                        "Please download credentials from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                
                try:
                    # Try to run local server (works on local machine)
                    print("Starting fresh authentication flow...")
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Could not run local server: {e}")
                    print("\n" + "="*60)
                    print("GMAIL AUTHENTICATION REQUIRED")
                    print("="*60)
                    print("Since we're running in Docker, you need to authenticate manually.")
                    print("\n1. Run this command on your HOST machine (not in Docker):")
                    print("   python3 authenticate_gmail.py")
                    print("\n2. Or, authenticate locally and copy the token.pickle file to this directory")
                    print("="*60)
                    raise Exception("Manual authentication required. See instructions above.")
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def get_messages(self, query: str = '', max_results: int = 10, 
                    user_id: str = 'me') -> List[Dict[str, Any]]:
        """
        Get messages from Gmail
        
        Args:
            query: Gmail search query (e.g., 'is:unread', 'from:example@gmail.com')
            max_results: Maximum number of messages to return
            user_id: Gmail user ID (default: 'me' for authenticated user)
            
        Returns:
            List of message dictionaries
        """
        try:
            # Search for messages
            results = self.service.users().messages().list(
                userId=user_id, q=query, maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full message details
            detailed_messages = []
            for message in messages:
                msg_detail = self.get_message_detail(message['id'], user_id)
                if msg_detail:
                    detailed_messages.append(msg_detail)
            
            return detailed_messages
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def get_message_detail(self, message_id: str, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific message
        
        Args:
            message_id: Gmail message ID
            user_id: Gmail user ID
            
        Returns:
            Message details dictionary
        """
        try:
            message = self.service.users().messages().get(
                userId=user_id, id=message_id, format='full'
            ).execute()
            
            # Extract message details
            headers = message['payload'].get('headers', [])
            header_dict = {h['name']: h['value'] for h in headers}
            
            # Get message body
            body = self._extract_message_body(message['payload'])
            
            # Parse date
            date_str = header_dict.get('Date', '')
            parsed_date = None
            if date_str:
                try:
                    parsed_date = datetime.fromtimestamp(mktime_tz(parsedate_tz(date_str)))
                except:
                    parsed_date = datetime.now()
            
            return {
                'id': message['id'],
                'thread_id': message['threadId'],
                'subject': header_dict.get('Subject', ''),
                'from': header_dict.get('From', ''),
                'to': header_dict.get('To', ''),
                'cc': header_dict.get('Cc', ''),
                'bcc': header_dict.get('Bcc', ''),
                'date': parsed_date.isoformat() if parsed_date else None,
                'body': body,
                'body_clean': EmailReplyParser.parse_reply(body) if body else '',
                'labels': message.get('labelIds', []),
                'snippet': message.get('snippet', ''),
                'is_unread': 'UNREAD' in message.get('labelIds', []),
                'is_important': 'IMPORTANT' in message.get('labelIds', []),
                'raw_headers': header_dict
            }
            
        except HttpError as error:
            print(f'An error occurred getting message {message_id}: {error}')
            return None
    
    def _extract_message_body(self, payload: Dict[str, Any]) -> str:
        """Extract message body from payload"""
        body = ''
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            # Simple message
            if payload['mimeType'] == 'text/plain':
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            elif payload['mimeType'] == 'text/html':
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def get_unread_messages(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get unread messages"""
        return self.get_messages(query='is:unread', max_results=max_results)
    
    def get_messages_from_sender(self, sender_email: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get messages from a specific sender"""
        return self.get_messages(query=f'from:{sender_email}', max_results=max_results)
    
    def get_messages_by_subject(self, subject: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get messages with specific subject"""
        return self.get_messages(query=f'subject:{subject}', max_results=max_results)
    
    def get_messages_in_date_range(self, start_date: datetime, end_date: datetime, 
                                  max_results: int = 10) -> List[Dict[str, Any]]:
        """Get messages within a date range"""
        start_str = start_date.strftime('%Y/%m/%d')
        end_str = end_date.strftime('%Y/%m/%d')
        query = f'after:{start_str} before:{end_str}'
        return self.get_messages(query=query, max_results=max_results)
    
    def mark_as_read(self, message_ids: List[str], user_id: str = 'me') -> bool:
        """Mark messages as read"""
        try:
            self.service.users().messages().batchModify(
                userId=user_id,
                body={
                    'ids': message_ids,
                    'removeLabelIds': ['UNREAD']
                }
            ).execute()
            return True
        except HttpError as error:
            print(f'An error occurred marking messages as read: {error}')
            return False
    
    def mark_as_unread(self, message_ids: List[str], user_id: str = 'me') -> bool:
        """Mark messages as unread"""
        try:
            self.service.users().messages().batchModify(
                userId=user_id,
                body={
                    'ids': message_ids,
                    'addLabelIds': ['UNREAD']
                }
            ).execute()
            return True
        except HttpError as error:
            print(f'An error occurred marking messages as unread: {error}')
            return False
    
    def get_user_profile(self, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            profile = self.service.users().getProfile(userId=user_id).execute()
            return {
                'email': profile['emailAddress'],
                'messages_total': profile['messagesTotal'],
                'threads_total': profile['threadsTotal'],
                'history_id': profile['historyId']
            }
        except HttpError as error:
            print(f'An error occurred getting profile: {error}')
            return None
    
    def search_emails(self, search_terms: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search emails with advanced search terms
        
        Args:
            search_terms: Search query (supports Gmail search operators)
            max_results: Maximum number of results
            
        Example search terms:
            - "from:example@gmail.com has:attachment"
            - "subject:meeting is:unread"
            - "older_than:7d"
        """
        return self.get_messages(query=search_terms, max_results=max_results)

    def send_sms_notification(self, phone_number: str, carrier: str, message: str) -> bool:
        """
        Send SMS notification using Gmail API and SMS gateways
        
        Args:
            phone_number: Phone number (digits only)
            carrier: Carrier name (att, verizon, tmobile, etc.)
            message: SMS message content
            
        Returns:
            True if successful, False otherwise
        """
        # SMS gateways mapping
        sms_gateways = {
            'att': '@txt.att.net',
            'verizon': '@vtext.com',
            'tmobile': '@tmomail.net',
            'sprint': '@messaging.sprintpcs.com',
            'boost': '@smsmyboostmobile.com',
            'cricket': '@sms.cricketwireless.net',
            'uscellular': '@email.uscc.net',
            'metropcs': '@mymetropcs.com'
        }
        
        if carrier.lower() not in sms_gateways:
            print(f"Unsupported carrier: {carrier}")
            return False
            
        to_email = f"{phone_number}{sms_gateways[carrier.lower()]}"
        
        try:
            # Create message
            msg = MIMEText(message)
            msg['Subject'] = ""  # SMS messages don't need subjects
            msg['From'] = "me"
            msg['To'] = to_email
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            
            # Send via Gmail API
            send_result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"SMS sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False


def authenticate_gmail(credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
    """
    Standalone function to authenticate Gmail API and create token.pickle file
    Run this on your local machine (not in Docker) to create the authentication token
    """
    import os
    import pickle
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    creds = None
    
    # Check if token file exists
    if os.path.exists(token_file):
        try:
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            print(f"⚠️  Warning: Could not load token file {token_file}: {e}")
            print("Removing invalid token file and re-authenticating...")
            os.remove(token_file)
            creds = None
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("🔄 Attempting to refresh expired token...")
                creds.refresh(Request())
                print("✅ Token refreshed successfully!")
            except Exception as e:
                print(f"⚠️  Token refresh failed: {e}")
                print("Removing invalid token file and starting fresh authentication...")
                # Remove the invalid token file
                if os.path.exists(token_file):
                    os.remove(token_file)
                creds = None
        
        # If we still don't have valid credentials, start fresh authentication
        if not creds or not creds.valid:
            if not os.path.exists(credentials_file):
                raise FileNotFoundError(
                    f"Gmail credentials file not found: {credentials_file}. "
                    "Please download credentials from Google Cloud Console."
                )
            
            print("🔐 Opening browser for Gmail authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
        
        print(f"✅ Authentication successful! Token saved to {token_file}")
        print(f"📋 Copy the {token_file} file to your Docker project directory")
    else:
        print("✅ Already authenticated!")
    
    return creds 