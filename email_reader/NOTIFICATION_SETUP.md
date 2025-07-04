# Notification System Setup Guide

Your email reader system now supports multiple notification methods to alert you about important emails or system events.

## 🚀 Quick Start (Gmail SMS)

The **easiest** way to get SMS notifications is using your existing Gmail authentication. **No passwords needed!**

### 1. Find Your Carrier's SMS Gateway

| Carrier      | SMS Gateway                |
| ------------ | -------------------------- |
| AT&T         | `@txt.att.net`             |
| Verizon      | `@vtext.com`               |
| T-Mobile     | `@tmomail.net`             |
| Sprint       | `@messaging.sprintpcs.com` |
| Boost Mobile | `@smsmyboostmobile.com`    |
| Cricket      | `@sms.cricketwireless.net` |
| US Cellular  | `@email.uscc.net`          |
| MetroPCS     | `@mymetropcs.com`          |

### 2. Set Up Environment Variables

Add these to your `.env` file:

```bash
GMAIL_SMS_PHONE_NUMBER=1234567890
GMAIL_SMS_CARRIER=tmobile
```

**Example:** If your phone number is `1234567890` and you have T-Mobile:

- Phone: `1234567890`
- Carrier: `tmobile`
- SMS address: `1234567890@tmomail.net`

### 3. Test Your Setup

```bash
python test_gmail_sms.py
```

Or use the API:

```bash
curl -X POST "http://localhost:8000/notifications/sms-gmail" \
  -d "phone_number=1234567890&carrier=tmobile&message=Test message!"
```

## 📱 All Notification Methods

### 1. Gmail SMS (Free!) ⭐ **Recommended**

**Setup:**

```bash
GMAIL_SMS_PHONE_NUMBER=1234567890
GMAIL_SMS_CARRIER=tmobile
```

**Usage:**

```python
from services.gmail_service import GmailService

gmail_service = GmailService()
success = gmail_service.send_sms_notification(
    phone_number="1234567890",
    carrier="tmobile",
    message="Alert: Important email received!"
)
```

### 2. Pushbullet (Free tier available)

**Setup:**

1. Get API key from [Pushbullet Settings](https://www.pushbullet.com/#settings)
2. Add to `.env`:
   ```bash
   PUSHBULLET_API_KEY=your-pushbullet-api-key
   ```

**Usage:**

```python
from services.notification_service import NotificationService, NotificationType

service = NotificationService()
service.send_notification(
    "New important email!",
    "Email Alert",
    [NotificationType.PUSHBULLET]
)
```

### 3. Discord Webhook (Free!)

**Setup:**

1. In Discord server: Settings > Integrations > Webhooks
2. Create webhook and copy URL
3. Add to `.env`:
   ```bash
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-url
   ```

### 4. Twilio SMS (Paid service)

**Setup:**

1. Sign up at [Twilio Console](https://console.twilio.com/)
2. Get phone number and credentials
3. Add to `.env`:
   ```bash
   TWILIO_ACCOUNT_SID=your-account-sid
   TWILIO_AUTH_TOKEN=your-auth-token
   TWILIO_FROM_NUMBER=+1234567890
   TWILIO_TO_NUMBER=+0987654321
   ```

### 5. Pushover (One-time fee)

**Setup:**

1. Get credentials from [Pushover](https://pushover.net/)
2. Add to `.env`:
   ```bash
   PUSHOVER_USER_KEY=your-user-key
   PUSHOVER_APP_TOKEN=your-app-token
   ```

### 6. Slack Webhook (Free!)

**Setup:**

1. Create Slack app with webhook
2. Add to `.env`:
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your-webhook-url
   ```

## 🔧 Usage Examples

### Basic Notification

```python
from services.notification_service import NotificationService

service = NotificationService()
service.send_notification(
    "Alert: Important email received!",
    "Email System"
)
```

### Multiple Methods

```python
from services.notification_service import NotificationType

service.send_notification(
    "Critical alert!",
    "System Monitor",
    [NotificationType.SMS_GMAIL, NotificationType.PUSHBULLET]
)
```

### Quick Notification

```python
from services.notification_service import send_quick_notification

send_quick_notification("Quick alert!", "System")
```

## 🌐 API Endpoints

### Check Status

```bash
GET /notifications/status
```

### Send Notification

```bash
POST /notifications/send
{
  "message": "Your notification message",
  "title": "Alert Title",
  "methods": ["sms_gmail", "pushbullet"]
}
```

### Test All Methods

```bash
POST /notifications/test
```

### Gmail SMS (Recommended)

```bash
POST /notifications/sms-gmail?phone_number=1234567890&carrier=tmobile&message=Test
```

### Get Supported Carriers

```bash
GET /notifications/carriers
```

## 🔍 Integration Examples

### Email Monitoring

```python
from services.gmail_service import GmailService

gmail = GmailService()
unread_emails = gmail.get_unread_messages(5)

for email in unread_emails:
    if "important" in email['subject'].lower():
        gmail.send_sms_notification(
            phone_number="1234567890",
            carrier="tmobile",
            message=f"Important email from {email['from']}: {email['subject']}"
        )
```

### Scheduled Monitoring

```python
import schedule
import time
from services.gmail_service import GmailService

def check_emails():
    gmail = GmailService()
    unread = gmail.get_unread_messages(1)
    if unread:
        gmail.send_sms_notification(
            "1234567890", "tmobile",
            f"New email: {unread[0]['subject']}"
        )

schedule.every(15).minutes.do(check_emails)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## 🛠️ Troubleshooting

### Common Issues

1. **Gmail Authentication Error**

   - Make sure you've run: `python3 authenticate_gmail.py`
   - Check that `token.pickle` file exists

2. **SMS Not Received**

   - Verify carrier is correct for your phone
   - Check phone number format (digits only)
   - Some carriers may have delays

3. **Environment Variables Not Working**
   - Restart Docker containers after adding variables
   - Check `.env` file format (no spaces around `=`)
   - Verify file is in project root

### Testing

```bash
# Test Gmail SMS (simplest)
python test_gmail_sms.py

# Test via API
curl -X GET "http://localhost:8000/notifications/status"

# Test specific method
curl -X POST "http://localhost:8000/notifications/test"
```

## 📊 Method Comparison

| Method        | Cost         | Setup Time | Passwords Needed | Reliability |
| ------------- | ------------ | ---------- | ---------------- | ----------- |
| **Gmail SMS** | Free         | 30 seconds | ❌ None          | High        |
| Pushbullet    | Free tier    | 2 minutes  | ❌ API key only  | High        |
| Discord       | Free         | 2 minutes  | ❌ Webhook only  | High        |
| Twilio        | Paid         | 10 minutes | ❌ API keys      | Very High   |
| Pushover      | One-time fee | 2 minutes  | ❌ API keys      | High        |
| Slack         | Free         | 3 minutes  | ❌ Webhook only  | High        |

## 🔐 Security Notes

- **Gmail SMS uses your existing authentication** - no additional passwords
- Use environment variables, never hardcode credentials
- Webhook URLs should be kept secret
- Consider using different credentials for different environments

## 🚀 Quick Start Summary

1. **Add to `.env`:**

   ```bash
   GMAIL_SMS_PHONE_NUMBER=1234567890
   GMAIL_SMS_CARRIER=tmobile
   ```

2. **Test:**

   ```bash
   python test_gmail_sms.py
   ```

3. **Use in code:**
   ```python
   from services.gmail_service import GmailService
   gmail = GmailService()
   gmail.send_sms_notification("1234567890", "tmobile", "Hello!")
   ```

That's it! No passwords, no complex setup - just works with your existing Gmail authentication! 🎉

For more examples, check the `test_gmail_sms.py` file!
