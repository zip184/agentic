# 🎮 Nintendo Switch 2 Email Monitor

**Never miss the Nintendo Switch 2 pre-order opportunity!**

This AI-powered email monitor automatically watches your Gmail for Nintendo emails about Switch 2 availability and alerts you instantly when the opportunity arises.

## 🚀 Quick Start

### 1. Ensure Your System is Running

```bash
# Make sure Docker containers are running
docker-compose up -d

# Check status
curl http://localhost:8000/nintendo/monitor/status
```

### 2. Configure Alert Methods

```bash
curl -X POST "http://localhost:8000/nintendo/monitor/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "check_interval_minutes": 15,
    "alert_configs": [
      {
        "method": "console",
        "target": "",
        "enabled": true
      },
      {
        "method": "file",
        "target": "nintendo_switch2_alerts.log",
        "enabled": true
      }
    ]
  }'
```

### 3. Test the Monitor

```bash
# Run a single check to make sure everything works
curl -X POST "http://localhost:8000/nintendo/monitor/test"
```

## 📧 How It Works

### **Smart Email Detection**

The monitor searches your Gmail for emails from Nintendo domains:

- `nintendo.com`
- `nintendo.co.jp`
- `nintendo-europe.com`
- `mynintendo.com`
- `nintendo.net`

### **AI-Powered Analysis**

When a Nintendo email is found, it:

1. **Scans for Switch 2 keywords**: "switch 2", "nintendo switch 2", "switch successor", etc.
2. **Looks for purchase indicators**: "pre-order", "available now", "buy now", "launch", etc.
3. **Uses OpenAI to analyze importance** and determine if it's a real purchase opportunity
4. **Remembers processed emails** to avoid duplicate alerts

### **Instant Alerts**

When the **PERFECT EMAIL** is detected (Switch 2 + purchase keywords), you get:

- 🚨 **HIGH PRIORITY ALERT**
- 📧 **Email details** (subject, sender, date)
- 🤖 **AI analysis** of the email content
- 💾 **Permanent memory storage** for future reference

## 🔧 Alert Configuration Options

### Console Alerts

```json
{
  "method": "console",
  "target": "",
  "enabled": true
}
```

Prints alerts directly to the console/logs.

### File Logging

```json
{
  "method": "file",
  "target": "nintendo_switch2_alerts.log",
  "enabled": true
}
```

Saves alerts to a file for permanent record.

### Webhook Alerts (Advanced)

```json
{
  "method": "webhook",
  "target": "https://your-webhook-url.com/nintendo-alert",
  "enabled": true
}
```

Sends HTTP POST requests to your webhook endpoint.

## 🔍 API Endpoints

### Check Monitor Status

```bash
GET /nintendo/monitor/status
```

Returns monitor configuration and statistics.

### Configure Alerts

```bash
POST /nintendo/monitor/configure
```

Set up alert methods and check intervals.

### Test Monitor

```bash
POST /nintendo/monitor/test
```

Run a single email check for testing.

### Start Monitoring (Demo)

```bash
POST /nintendo/monitor/start
```

Runs one monitoring cycle (in production, this would run continuously).

## 🎯 Example Alert Output

When a Switch 2 purchase email is detected:

```
============================================================
🎮 NINTENDO SWITCH 2 EMAIL DETECTED! 🚨

Subject: Nintendo Switch 2 - Pre-Orders Now Open!
From: nintendo@nintendo.com
Date: 2024-12-22T09:00:00Z
============================================================
AI Analysis: This email from Nintendo announces the official
pre-order opening for the Nintendo Switch 2 console. The
email contains direct purchase links and indicates limited
availability. IMMEDIATE ACTION RECOMMENDED.
```

## 🔧 Monitoring Schedule

The monitor checks for new emails every **15 minutes** by default (configurable). It:

- Only searches emails from the **last 24 hours** to avoid processing old emails
- Uses **memory system** to track processed emails
- Provides **different alert levels** for mentions vs. actual purchase opportunities

### High Priority Alerts (🚨)

- Contains Switch 2 keywords **AND** purchase keywords
- Gets AI analysis for verification
- Triggers all configured alert methods

### Medium Priority Alerts (📧)

- Contains Switch 2 keywords but no purchase indicators
- Limited to console/file alerts only
- Useful for tracking Nintendo communications

## 💡 Pro Tips

1. **Set Multiple Alert Methods**: Use both console and file logging so you have a permanent record.

2. **Monitor the Logs**: Check Docker logs to see monitoring activity:

   ```bash
   docker-compose logs app --tail=20
   ```

3. **Test Regularly**: Run the test endpoint occasionally to ensure everything is working.

4. **Check Your Gmail**: Make sure you're subscribed to Nintendo newsletters and your Gmail is accessible.

5. **Customize Keywords**: The monitor looks for various Switch 2 terms, but you can modify the keywords in the source code if needed.

## 🛠️ Advanced Usage

### Webhook Integration

Set up a webhook to receive alerts in Slack, Discord, or other services:

```python
# Example webhook receiver
@app.route('/nintendo-alert', methods=['POST'])
def handle_nintendo_alert():
    data = request.json
    if data['urgency'] == 'HIGH':
        # Send urgent notification
        send_slack_message(f"🚨 SWITCH 2 ALERT: {data['data']['subject']}")
    return "OK"
```

### Custom Alert Logic

You can modify `services/nintendo_monitor.py` to add:

- Additional email providers
- More sophisticated keyword matching
- Custom AI prompts for better analysis
- Integration with other notification services

## 📊 Monitoring Statistics

Check `/nintendo/monitor/status` to see:

- Last check timestamp
- Configured alert methods
- Memory system statistics
- Keyword lists being monitored

## 🚨 When You Get The Alert

**IMMEDIATE ACTIONS:**

1. **Check your email** - Open Gmail and look for the Nintendo email
2. **Verify the alert** - Make sure it's legitimate (not spam)
3. **Act quickly** - Nintendo pre-orders often sell out fast!
4. **Follow the links** - Use the official Nintendo purchase links
5. **Spread the word** - Let your friends know too!

---

**Happy Gaming! 🎮**

_This monitor gives you the edge you need to secure your Nintendo Switch 2 as soon as it becomes available._
