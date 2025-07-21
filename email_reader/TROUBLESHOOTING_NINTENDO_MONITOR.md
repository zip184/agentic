# 🔧 Nintendo Monitor Troubleshooting Guide

## Quick Health Check Commands

### 1. Check Service Status

```bash
curl http://localhost:8000/nintendo/monitor/status
```

**Expected**: JSON response with `"status": "available"`

### 2. Test the Monitor

```bash
curl -X POST http://localhost:8000/nintendo/monitor/test
```

**Expected**: `{"message":"Nintendo monitor test completed successfully"}`

### 3. Check Docker Containers

```bash
cd /Users/btillinghast/sandbox/agentic/email_reader
docker-compose ps
```

**Expected**: All containers should be "Up"

## Common Issues & Solutions

### 🔴 Issue: "Connection refused" or endpoint unresponsive

**Step 1: Check if containers are running**

```bash
docker-compose ps
```

**Step 2: If containers are down, restart them**

```bash
docker-compose down
docker-compose up -d
```

**Step 3: Check logs for errors**

```bash
docker-compose logs app --tail=20
```

### 🔴 Issue: Service starts but fails requests

**Check application logs**

```bash
docker-compose logs app --follow
```

Look for error messages about:

- OpenAI API key issues
- Gmail authentication problems
- ChromaDB connection failures

**Restart specific service**

```bash
docker-compose restart app
```

### 🔴 Issue: Monitor works but no notifications

**Check Pushover configuration**

```bash
curl http://localhost:8000/notifications/status
```

**Test notifications manually**

```bash
curl -X POST "http://localhost:8000/notifications/test"
```

### 🔴 Issue: Cron job not running

**Check cron status**

```bash
make cron-status
```

**Check cron logs**

```bash
make cron-logs
```

**Reinstall cron job**

```bash
make cron-start
```

## System Recovery Commands

### Full System Restart

```bash
# Navigate to project directory
cd /Users/btillinghast/sandbox/agentic/email_reader

# Stop all services
docker-compose down

# Clear any orphaned containers
docker-compose down --remove-orphans

# Restart everything
docker-compose up -d

# Wait 30 seconds for services to start
sleep 30

# Test the system
curl -X POST http://localhost:8000/nintendo/monitor/test
```

### Emergency Manual Test

```bash
# Run the monitor script directly
./scripts/nintendo-monitor.sh --test --verbose
```

## Performance Monitoring

### Check recent activity

```bash
# App logs
docker-compose logs app --tail=50

# Cron logs
tail -f /tmp/nintendo_monitor.log
```

### Monitor resource usage

```bash
# Container resource usage
docker stats email_reader-app-1 --no-stream

# Disk space
df -h
```

## Configuration Verification

### Environment Variables

```bash
# Check if required environment variables are set
docker-compose exec app env | grep -E "(OPENAI|PUSHOVER|GMAIL)"
```

### Gmail Authentication

```bash
# Test Gmail connection
curl -X POST "http://localhost:8000/gmail/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "from:nintendo.com", "max_results": 1}'
```

## Contact Information

If issues persist:

1. Check the Docker logs first
2. Verify your `.env` file has all required API keys
3. Ensure Gmail authentication is working
4. Try restarting the entire system

## Quick Reference

| Command                                             | Purpose               |
| --------------------------------------------------- | --------------------- |
| `make up`                                           | Start all services    |
| `make down`                                         | Stop all services     |
| `make cron-status`                                  | Check cron job status |
| `make cron-logs`                                    | View monitoring logs  |
| `curl localhost:8000/nintendo/monitor/status`       | Health check          |
| `curl -X POST localhost:8000/nintendo/monitor/test` | Test monitor          |

---

_Last updated: $(date)_
