# Nintendo Switch 2 Alert System

**Never miss the Nintendo Switch 2 pre-order opportunity!**

An AI-powered email monitoring system that automatically watches your Gmail for Nintendo Switch 2 announcements and sends instant notifications to your phone via Pushover.

## Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📋 Prerequisites](#-prerequisites)
- [⚙️ Installation](#️-installation)
- [🔧 Configuration](#-configuration)
- [🎮 Nintendo Switch 2 Monitoring](#-nintendo-switch-2-monitoring)
  - [Manual Testing](#manual-testing)
  - [Automated Monitoring with Cron](#automated-monitoring-with-cron)
  - [How It Works](#how-it-works)
- [🔔 Notification System](#-notification-system)
- [🧠 AI Memory System](#-ai-memory-system)
- [📧 Gmail Integration](#-gmail-integration)
- [🛠️ Development](#️-development)
- [📖 API Reference](#-api-reference)
- [🔍 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Features

- **🎮 Nintendo Switch 2 Email Detection**: AI-powered monitoring of Gmail for Switch 2 announcements
- **🔔 Instant Notifications**: Pushover notifications sent directly to your phone
- **🧠 Smart Memory System**: Persistent vector-based memory using ChromaDB
- **📧 Gmail Integration**: Full Gmail API access with OAuth authentication
- **🤖 AI Analysis**: OpenAI-powered email importance analysis
- **⏰ Automated Monitoring**: Cron job support for continuous monitoring
- **🔍 Semantic Search**: Find relevant memories and emails using embeddings
- **🔗 REST API**: Full API for all system interactions

## 🚀 Quick Start

**Get up and running in 5 minutes:**

1. **Clone and start the system:**

   ```bash
   git clone <repository_url>
   cd email_reader
   make up
   ```

2. **Set up Pushover notifications:**

   - Create account at [pushover.net](https://pushover.net)
   - Get your User Key and create an Application Token
   - Add to `.env` file:
     ```
     PUSHOVER_USER_KEY=your_user_key
     PUSHOVER_APP_TOKEN=your_app_token
     ```

3. **Test the system:**

   ```bash
   # Test notifications
   curl -X POST "http://localhost:8000/notifications/send" \
     -H "Content-Type: application/json" \
     -d '{"message": "Test notification!", "title": "Nintendo Monitor", "methods": ["pushover"]}'

   # Test Nintendo monitor
   curl -X POST http://localhost:8000/nintendo/monitor/test
   ```

4. **Set up automated monitoring:**
   ```bash
   # Add to cron (every 15 minutes)
   crontab -e
   # Add this line:
   */15 * * * * curl -s -X POST http://localhost:8000/nintendo/monitor/start >> /tmp/nintendo_monitor.log 2>&1
   ```

**You're now monitoring for Nintendo Switch 2 announcements!** 🎮

## 📋 Prerequisites

- **Docker & Docker Compose**
- **OpenAI API Key** (for AI analysis)
- **Gmail Account** (for email monitoring)
- **Pushover Account** (for notifications)

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <repository_url>
cd email_reader
```

### 2. Environment Setup

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=your_openai_api_key

# Pushover Notifications (Recommended)
PUSHOVER_USER_KEY=your_pushover_user_key
PUSHOVER_APP_TOKEN=your_pushover_app_token

# Optional: Other notification methods
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_FROM_NUMBER=your_twilio_number
TWILIO_TO_NUMBER=your_phone_number
DISCORD_WEBHOOK_URL=your_discord_webhook
SLACK_WEBHOOK_URL=your_slack_webhook
```

### 3. Start the System

```bash
# Using make (recommended)
make up

# Or using docker-compose directly
docker-compose up -d
```

### 4. Gmail Authentication

Run the Gmail authentication script:

```bash
python3 authenticate_gmail.py
```

The system will be available at `http://localhost:8000`.

## 🔧 Configuration

### Environment Variables

| Variable              | Description                    | Required    |
| --------------------- | ------------------------------ | ----------- |
| `OPENAI_API_KEY`      | OpenAI API key for AI analysis | Yes         |
| `PUSHOVER_USER_KEY`   | Pushover user key              | Recommended |
| `PUSHOVER_APP_TOKEN`  | Pushover application token     | Recommended |
| `TWILIO_ACCOUNT_SID`  | Twilio account SID             | Optional    |
| `TWILIO_AUTH_TOKEN`   | Twilio auth token              | Optional    |
| `TWILIO_FROM_NUMBER`  | Twilio phone number            | Optional    |
| `TWILIO_TO_NUMBER`    | Your phone number              | Optional    |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL            | Optional    |
| `SLACK_WEBHOOK_URL`   | Slack webhook URL              | Optional    |

### Memory System Configuration

The memory system uses ChromaDB for persistent vector storage:

```python
from memory import ChromaMemoryManager

# Custom configuration
memory_manager = ChromaMemoryManager(
    persist_directory="./custom_chroma_db",
    collection_name="my_agent_memories"
)
```

## 🎮 Nintendo Switch 2 Monitoring

The core feature of this system - never miss the Nintendo Switch 2 announcement!

### Manual Testing

```bash
# Test the Nintendo monitor
curl -X POST http://localhost:8000/nintendo/monitor/test

# Check monitor status
curl http://localhost:8000/nintendo/monitor/status

# Test Pushover notifications
curl -X POST "http://localhost:8000/notifications/send" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test notification!", "title": "Nintendo Monitor", "methods": ["pushover"]}'
```

### Automated Monitoring with Cron

The recommended approach for continuous monitoring:

#### Basic Setup (Every 15 Minutes)

```bash
# Edit your crontab
crontab -e

# Add this line for basic monitoring
*/15 * * * * curl -s -X POST http://localhost:8000/nintendo/monitor/start > /dev/null 2>&1
```

#### Recommended Setup (With Logging)

```bash
# Check every 15 minutes with logging
*/15 * * * * curl -s -X POST http://localhost:8000/nintendo/monitor/start >> /tmp/nintendo_monitor.log 2>&1
```

#### Alternative Schedules

```bash
# Every 5 minutes (aggressive monitoring)
*/5 * * * * curl -s -X POST http://localhost:8000/nintendo/monitor/start >> /tmp/nintendo_monitor.log 2>&1

# Every 30 minutes (conservative)
*/30 * * * * curl -s -X POST http://localhost:8000/nintendo/monitor/start >> /tmp/nintendo_monitor.log 2>&1

# Business hours only (9 AM - 6 PM, Monday-Friday)
*/15 9-18 * * 1-5 curl -s -X POST http://localhost:8000/nintendo/monitor/start >> /tmp/nintendo_monitor.log 2>&1
```

#### Cron Management

```bash
# List current cron jobs
crontab -l

# Edit cron jobs
crontab -e

# Remove all cron jobs
crontab -r

# Monitor your logs
tail -f /tmp/nintendo_monitor.log
```

### How It Works

1. **🔍 Email Scanning**: Monitors Gmail for emails from Nintendo domains
2. **🎯 Keyword Detection**: Looks for "Switch 2" + purchase terms ("pre-order", "buy now", etc.)
3. **🤖 AI Analysis**: Uses OpenAI to determine email importance
4. **🚨 Instant Alert**: Sends Pushover notification to your phone
5. **💾 Memory Storage**: Remembers processed emails to avoid duplicates

**Example Alert:**

```
🎮 NINTENDO SWITCH 2 EMAIL DETECTED! 🚨

Subject: Nintendo Switch 2 - Pre-Orders Now Open!
From: nintendo@nintendo.com
Date: 2024-12-22T09:00:00Z

AI Analysis: This email announces official pre-order
opening for Nintendo Switch 2. IMMEDIATE ACTION RECOMMENDED!
```

**Monitored Domains:**

- nintendo.com
- nintendo.co.jp
- nintendo-europe.com
- mynintendo.com
- nintendo.net

## 🔔 Notification System

Multiple notification methods supported:

### Pushover (Recommended)

- **Setup**: Create account at [pushover.net](https://pushover.net)
- **Pros**: Reliable, instant, works on all devices
- **Configuration**: Add `PUSHOVER_USER_KEY` and `PUSHOVER_APP_TOKEN` to `.env`

### Twilio SMS

- **Setup**: Create account at [twilio.com](https://twilio.com)
- **Configuration**: Add Twilio credentials to `.env`

### Discord/Slack Webhooks

- **Setup**: Create webhook in your Discord/Slack workspace
- **Configuration**: Add webhook URL to `.env`

### Test Notifications

```bash
# Test all configured methods
curl -X POST http://localhost:8000/notifications/test

# Test specific method
curl -X POST "http://localhost:8000/notifications/send" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test!", "methods": ["pushover"]}'
```

## 🧠 AI Memory System

Persistent vector-based memory using ChromaDB for intelligent email processing:

### Memory Types

- **observation**: Things the system has observed
- **action**: Actions the system has taken
- **goal**: Goals the system has pursued
- **reflection**: System reflections and insights
- **learning**: Lessons learned from experiences
- **context**: Contextual information

### Usage Examples

```python
from agents.memory_agent import MemoryAwareAgent

agent = MemoryAwareAgent()

# Add memories
agent.add_observation("Nintendo emails often arrive on Tuesdays", importance_score=0.8)
agent.add_learning("Pre-order emails contain 'limited availability' keywords", importance_score=0.9)

# Search memories
memories = agent.search_memories("Nintendo email patterns", limit=5)

# Get statistics
stats = agent.get_memory_stats()
```

### API Endpoints

```bash
# Add memory
curl -X POST "http://localhost:8000/memory/add" \
  -H "Content-Type: application/json" \
  -d '{"content": "Nintendo emails peak on Tuesdays", "memory_type": "observation"}'

# Search memories
curl -X POST "http://localhost:8000/memory/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "Nintendo patterns", "limit": 10}'

# Get statistics
curl http://localhost:8000/memory/stats
```

## 📧 Gmail Integration

Full Gmail API integration with OAuth authentication:

### Setup

1. **Authenticate**: Run `python3 authenticate_gmail.py`
2. **Grant Permissions**: Follow the OAuth flow
3. **Test**: `curl http://localhost:8000/gmail/status`

### Available Operations

```bash
# Get Gmail profile
curl http://localhost:8000/gmail/profile

# Search emails
curl -X POST "http://localhost:8000/gmail/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "from:nintendo.com", "max_results": 10}'

# Get unread emails
curl http://localhost:8000/gmail/unread

# Process and analyze emails with AI
curl -X POST "http://localhost:8000/gmail/process-and-analyze" \
  -H "Content-Type: application/json" \
  -d '{"email_query": "from:nintendo.com", "max_emails": 5}'
```

## 🛠️ Development

### Development Workflow

This project uses `make` to simplify Docker Compose commands:

```bash
# Get help
make help

# Start services
make up

# Stop services
make down

# Rebuild and restart
make rebuild

# View logs
make logs

# Check status
make status
```

### Raw Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Check status
docker-compose ps
```

### File Structure

```
email_reader/
├── agents/                    # AI agents
│   ├── agent.py              # Basic agent
│   └── memory_agent.py       # Memory-aware agent
├── app/                      # FastAPI application
│   └── main.py              # API endpoints
├── memory/                   # Memory system
│   ├── chroma_memory.py     # ChromaDB manager
│   └── memory_types.py      # Memory type definitions
├── services/                 # Core services
│   ├── gmail_service.py     # Gmail integration
│   ├── nintendo_monitor.py  # Nintendo monitoring
│   └── notification_service.py # Notifications
├── docker-compose.yml        # Docker configuration
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 📖 API Reference

Full API documentation available at `http://localhost:8000/docs` when running.

### Core Endpoints

| Endpoint                   | Method | Description                       |
| -------------------------- | ------ | --------------------------------- |
| `/nintendo/monitor/test`   | POST   | Test Nintendo monitor             |
| `/nintendo/monitor/start`  | POST   | Run Nintendo monitor (production) |
| `/nintendo/monitor/status` | GET    | Get monitor status                |
| `/notifications/send`      | POST   | Send notification                 |
| `/notifications/test`      | POST   | Test all notification methods     |
| `/memory/add`              | POST   | Add memory                        |
| `/memory/search`           | POST   | Search memories                   |
| `/gmail/search`            | POST   | Search Gmail                      |
| `/run-with-memory`         | POST   | Run AI agent with memory          |

### Nintendo Monitor Endpoints

- `GET /nintendo/monitor/status` - Get monitor status
- `POST /nintendo/monitor/test` - Test monitor
- `POST /nintendo/monitor/start` - Run monitor (for cron jobs)
- `POST /nintendo/monitor/configure` - Configure alert methods

### Notification Endpoints

- `GET /notifications/status` - Get available notification methods
- `POST /notifications/send` - Send notification
- `POST /notifications/test` - Test all methods

### Memory Endpoints

- `POST /memory/add` - Add memory
- `POST /memory/search` - Search memories
- `GET /memory/stats` - Get memory statistics
- `POST /memory/clear` - Clear all memories

## 🔍 Troubleshooting

### Common Issues

**🔴 Cron job not running?**

- Check containers: `docker-compose ps`
- Test API manually: `curl http://localhost:8000/nintendo/monitor/status`
- Check cron logs: `tail /tmp/nintendo_monitor.log`

**🔴 No Nintendo emails found?**

- Verify Gmail authentication: `curl http://localhost:8000/gmail/status`
- Check if subscribed to Nintendo newsletters
- Test Gmail search: `curl -X POST "http://localhost:8000/gmail/search" -H "Content-Type: application/json" -d '{"query": "from:nintendo.com"}'`

**🔴 Pushover notifications not working?**

- Test directly: `curl -X POST http://localhost:8000/notifications/test`
- Verify environment variables are set
- Check Pushover app is installed on your phone
- Verify User Key and App Token are correct

**🔴 Memory system issues?**

- Check ChromaDB container: `docker-compose logs chroma`
- Clear memory if corrupted: `curl -X POST http://localhost:8000/memory/clear`
- Check memory stats: `curl http://localhost:8000/memory/stats`

**🔴 Gmail authentication problems?**

- Re-run: `python3 authenticate_gmail.py`
- Check if `token.json` exists
- Verify OAuth scopes include Gmail access

### Debug Commands

```bash
# Check all service status
curl http://localhost:8000/nintendo/monitor/status
curl http://localhost:8000/notifications/status
curl http://localhost:8000/gmail/status
curl http://localhost:8000/memory/stats

# View logs
docker-compose logs app
tail -f /tmp/nintendo_monitor.log

# Test individual components
curl -X POST http://localhost:8000/nintendo/monitor/test
curl -X POST http://localhost:8000/notifications/test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/email_reader.git
cd email_reader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Start development server
make up
```

## 📄 License

MIT License - see LICENSE file for details.

---

**🎮 Ready to catch the Nintendo Switch 2 announcement? Set up your monitoring system now!**
