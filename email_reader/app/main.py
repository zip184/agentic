import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from agents.agent import run_agent
from agents.memory_agent import MemoryAwareAgent
from memory import MemoryType, ChromaMemoryManager
from services.gmail_service import GmailService
from services.nintendo_monitor import NintendoSwitch2Monitor, AlertConfig
from services.notification_service import NotificationService, NotificationType, send_quick_notification
# from services.scheduler_service import SchedulerService, JobConfig  # Disabled - using external cron instead

app = FastAPI(title="Autonomous Agent API with Memory", version="1.0.0")

# Initialize the memory-aware agent
memory_agent = MemoryAwareAgent()

# Initialize Gmail service (will be None if credentials not available)
try:
    gmail_service = GmailService()
    print("Gmail service initialized successfully")
except Exception as e:
    gmail_service = None
    print(f"Gmail service not available: {e}")

# Initialize Nintendo Switch 2 Monitor
nintendo_monitor = None
if gmail_service:
    try:
        nintendo_monitor = NintendoSwitch2Monitor(gmail_service, memory_agent.memory_manager)
        print("Nintendo Switch 2 monitor initialized successfully")
    except Exception as e:
        print(f"Nintendo monitor initialization failed: {e}")

# Initialize Notification Service
try:
    notification_service = NotificationService(gmail_service=gmail_service)
    print("Notification service initialized successfully")
except Exception as e:
    notification_service = None
    print(f"Notification service initialization failed: {e}")

# Initialize Scheduler Service - DISABLED (using external cron instead)
# try:
#     scheduler_service = SchedulerService(gmail_service=gmail_service, nintendo_monitor=nintendo_monitor)
#     scheduler_service.start_scheduler()
#     print("Scheduler service initialized successfully")
# except Exception as e:
#     scheduler_service = None
#     print(f"Scheduler service initialization failed: {e}")
scheduler_service = None  # Disabled

class AgentRequest(BaseModel):
    goal: str
    context: Optional[str] = ""
    memory_search_limit: Optional[int] = 5

class MemoryRequest(BaseModel):
    content: str
    memory_type: MemoryType
    importance_score: Optional[float] = 0.5
    metadata: Optional[Dict[str, Any]] = None

class MemorySearchRequest(BaseModel):
    query: str
    memory_type: Optional[MemoryType] = None
    limit: Optional[int] = 10

class GmailSearchRequest(BaseModel):
    query: Optional[str] = ""
    max_results: Optional[int] = 10
    
class GmailDateRangeRequest(BaseModel):
    start_date: str  # ISO format date string
    end_date: str    # ISO format date string
    max_results: Optional[int] = 10

class EmailProcessingRequest(BaseModel):
    email_query: str = "is:unread"
    max_emails: Optional[int] = 5
    store_in_memory: Optional[bool] = True
    analyze_with_agent: Optional[bool] = True

class AlertConfigRequest(BaseModel):
    method: str  # 'console', 'webhook', 'email', 'file'
    target: str  # URL for webhook, email address, file path, etc.
    enabled: Optional[bool] = True

class MonitorConfigRequest(BaseModel):
    check_interval_minutes: Optional[int] = 15
    alert_configs: List[AlertConfigRequest] = []

class NotificationRequest(BaseModel):
    message: str
    title: Optional[str] = "Notification"
    methods: Optional[List[str]] = None  # List of notification method names

# Scheduler classes disabled - using external cron instead
# class SchedulerJobRequest(BaseModel):
#     id: str
#     name: str
#     description: str
#     endpoint: str
#     schedule_type: str  # 'interval' or 'cron'
#     schedule_value: str  # '15' for 15 minutes, or '*/15 * * * *' for cron
#     enabled: Optional[bool] = True

# class NintendoMonitorJobRequest(BaseModel):
#     interval_minutes: Optional[int] = 15
#     cron_expression: Optional[str] = None  # If provided, uses cron instead of interval



@app.get("/")
def root():
    return {"message": "Autonomous Agent API with ChromaDB Memory running"}

@app.get("/testout")
def test_out():
    return {"output": "Test response 2"}

@app.post("/run")
def run_task(request: AgentRequest):
    """Run the basic agent without memory"""
    result = run_agent(request.goal)
    return {"result": result}

@app.post("/run-with-memory")
def run_task_with_memory(request: AgentRequest):
    """Run the memory-aware agent"""
    try:
        result = memory_agent.run_agent(
            goal=request.goal,
            current_context=request.context,
            memory_search_limit=request.memory_search_limit
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/add")
def add_memory(request: MemoryRequest):
    """Add a new memory entry"""
    try:
        memory_id = memory_agent.memory_manager.add_memory(
            content=request.content,
            memory_type=request.memory_type,
            importance_score=request.importance_score,
            metadata=request.metadata
        )
        return {"memory_id": memory_id, "message": "Memory added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/search")
def search_memories(request: MemorySearchRequest):
    """Search for relevant memories"""
    try:
        memories = memory_agent.search_memories(
            query=request.query,
            memory_type=request.memory_type,
            limit=request.limit
        )
        return {
            "memories": [
                {
                    "id": memory.id,
                    "content": memory.content,
                    "memory_type": memory.memory_type.value,
                    "timestamp": memory.timestamp.isoformat(),
                    "importance_score": memory.importance_score,
                    "metadata": memory.metadata
                }
                for memory in memories
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/stats")
def get_memory_stats():
    """Get memory statistics"""
    try:
        stats = memory_agent.get_memory_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/type/{memory_type}")
def get_memories_by_type(memory_type: str, limit: int = 100):
    """Get all memories of a specific type"""
    try:
        memory_type_enum = MemoryType(memory_type)
        memories = memory_agent.get_memories_by_type(memory_type_enum, limit)
        return {
            "memories": [
                {
                    "id": memory.id,
                    "content": memory.content,
                    "memory_type": memory.memory_type.value,
                    "timestamp": memory.timestamp.isoformat(),
                    "importance_score": memory.importance_score,
                    "metadata": memory.metadata
                }
                for memory in memories
            ]
        }
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid memory type: {memory_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/clear")
def clear_all_memories():
    """Clear all memories"""
    try:
        result = memory_agent.memory_manager.clear_all_memories_detailed()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Convenience endpoints for different memory types
@app.post("/memory/observation")
def add_observation(content: str, importance_score: float = 0.5, metadata: Optional[Dict[str, Any]] = None):
    """Add an observation to memory"""
    try:
        memory_agent.add_observation(content, importance_score, metadata)
        return {"message": "Observation added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/learning")
def add_learning(content: str, importance_score: float = 0.8, metadata: Optional[Dict[str, Any]] = None):
    """Add a learning to memory"""
    try:
        memory_agent.add_learning(content, importance_score, metadata)
        return {"message": "Learning added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/reflection")
def add_reflection(content: str, importance_score: float = 0.7, metadata: Optional[Dict[str, Any]] = None):
    """Add a reflection to memory"""
    try:
        memory_agent.add_reflection(content, importance_score, metadata)
        return {"message": "Reflection added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Gmail API Endpoints
@app.get("/gmail/status")
def gmail_status():
    """Check if Gmail service is available"""
    if gmail_service is None:
        return {"status": "unavailable", "message": "Gmail credentials not configured"}
    
    try:
        profile = gmail_service.get_user_profile()
        return {"status": "available", "profile": profile}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/gmail/profile")
def get_gmail_profile():
    """Get Gmail profile information"""
    if gmail_service is None:
        raise HTTPException(status_code=503, detail="Gmail service not available")
    
    try:
        profile = gmail_service.get_user_profile()
        if profile is None:
            raise HTTPException(status_code=500, detail="Could not fetch profile")
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gmail/messages")
def get_gmail_messages(request: GmailSearchRequest):
    """Get Gmail messages with optional query"""
    if gmail_service is None:
        raise HTTPException(status_code=503, detail="Gmail service not available")
    
    try:
        messages = gmail_service.get_messages(
            query=request.query,
            max_results=request.max_results
        )
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gmail/unread")
def get_unread_messages(max_results: int = 10):
    """Get unread Gmail messages"""
    if gmail_service is None:
        raise HTTPException(status_code=503, detail="Gmail service not available")
    
    try:
        messages = gmail_service.get_unread_messages(max_results=max_results)
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gmail/from/{sender_email}")
def get_messages_from_sender(sender_email: str, max_results: int = 10):
    """Get messages from a specific sender"""
    if gmail_service is None:
        raise HTTPException(status_code=503, detail="Gmail service not available")
    
    try:
        messages = gmail_service.get_messages_from_sender(
            sender_email=sender_email,
            max_results=max_results
        )
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gmail/date-range")
def get_messages_by_date_range(request: GmailDateRangeRequest):
    """Get messages within a date range"""
    if gmail_service is None:
        raise HTTPException(status_code=503, detail="Gmail service not available")
    
    try:
        start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
        
        messages = gmail_service.get_messages_in_date_range(
            start_date=start_date,
            end_date=end_date,
            max_results=request.max_results
        )
        return {"messages": messages, "count": len(messages)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gmail/search")
def search_gmail_messages(request: GmailSearchRequest):
    """Search Gmail messages with advanced queries"""
    if gmail_service is None:
        raise HTTPException(status_code=503, detail="Gmail service not available")
    
    try:
        messages = gmail_service.search_emails(
            search_terms=request.query,
            max_results=request.max_results
        )
        return {"messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gmail/process-and-analyze")
def process_emails_with_agent(request: EmailProcessingRequest):
    """Fetch emails and analyze them with the memory-aware agent"""
    if gmail_service is None:
        raise HTTPException(status_code=503, detail="Gmail service not available")
    
    try:
        # Fetch emails
        messages = gmail_service.get_messages(
            query=request.email_query,
            max_results=request.max_emails
        )
        
        results = []
        
        for message in messages:
            # Store email in memory if requested
            if request.store_in_memory:
                # Limit content length for memory storage
                body_preview = message['body_clean'][:1000] if message['body_clean'] else ""
                email_content = f"Email from {message['from']}: {message['subject']}\n\n{body_preview}"
                memory_agent.add_observation(
                    observation=email_content,
                    importance_score=0.6,
                    metadata={
                        "source": "gmail",
                        "message_id": message['id'],
                        "subject": message['subject'],
                        "from": message['from'],
                        "date": message['date']
                    }
                )
            
            # Analyze with agent if requested
            analysis = None
            if request.analyze_with_agent:
                goal = f"Analyze this email and provide insights: {message['subject']}"
                # Limit context to avoid token limits - very short summary
                body_preview = message['body_clean'][:200] if message['body_clean'] else ""
                context = f"From: {message['from']}\nSubject: {message['subject']}\nContent: {body_preview}"
                analysis = memory_agent.run_agent(goal=goal, current_context=context)
            
            results.append({
                "message": message,
                "analysis": analysis,
                "stored_in_memory": request.store_in_memory
            })
        
        return {
            "processed_emails": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Nintendo Switch 2 Monitoring Endpoints
@app.get("/nintendo/monitor/status")
def get_nintendo_monitor_status():
    """Get Nintendo Switch 2 monitor status"""
    if nintendo_monitor is None:
        return {"status": "unavailable", "message": "Nintendo monitor not initialized"}
    
    try:
        stats = nintendo_monitor.get_monitoring_stats()
        return {"status": "available", "stats": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/nintendo/monitor/configure")
def configure_nintendo_monitor(request: MonitorConfigRequest):
    """Configure Nintendo Switch 2 monitor alerts"""
    if nintendo_monitor is None:
        raise HTTPException(status_code=503, detail="Nintendo monitor not available")
    
    try:
        # Clear existing alert configs
        nintendo_monitor.alert_configs.clear()
        
        # Add new alert configs
        for alert_config in request.alert_configs:
            config = AlertConfig(
                method=alert_config.method,
                target=alert_config.target,
                enabled=alert_config.enabled
            )
            nintendo_monitor.add_alert_config(config)
        
        return {
            "message": "Nintendo monitor configured successfully",
            "alert_configs": len(request.alert_configs),
            "check_interval": request.check_interval_minutes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nintendo/monitor/start")
def start_nintendo_monitor(check_interval_minutes: int = 15):
    """Start Nintendo Switch 2 monitoring (this would typically run in background)"""
    if nintendo_monitor is None:
        raise HTTPException(status_code=503, detail="Nintendo monitor not available")
    
    # Note: In a real implementation, this would start a background task
    # For demo purposes, we'll just run one check
    try:
        import asyncio
        
        async def run_check():
            await nintendo_monitor._check_for_switch2_emails()
        
        asyncio.run(run_check())
        
        return {
            "message": "Nintendo monitor check completed",
            "note": "In production, this would start continuous monitoring"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nintendo/monitor/test")
def test_nintendo_monitor():
    """Test Nintendo Switch 2 monitor with current emails"""
    if nintendo_monitor is None:
        raise HTTPException(status_code=503, detail="Nintendo monitor not available")
    
    try:
        import asyncio
        
        async def run_test():
            await nintendo_monitor._check_for_switch2_emails()
        
        asyncio.run(run_test())
        
        return {"message": "Nintendo monitor test completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Notification Endpoints
@app.get("/notifications/status")
def get_notification_status():
    """Get notification service status and available methods"""
    if notification_service is None:
        return {"status": "unavailable", "message": "Notification service not initialized"}
    
    try:
        available_methods = notification_service._get_available_methods()
        return {
            "status": "available",
            "available_methods": [method.value for method in available_methods],
            "supported_carriers": list(notification_service.SMS_GATEWAYS.keys())
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/notifications/send")
def send_notification(request: NotificationRequest):
    """Send a notification via configured methods"""
    if notification_service is None:
        raise HTTPException(status_code=503, detail="Notification service not available")
    
    try:
        # Convert string method names to NotificationType enums
        methods = None
        if request.methods:
            methods = []
            for method_name in request.methods:
                try:
                    method_enum = NotificationType(method_name)
                    methods.append(method_enum)
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid notification method: {method_name}")
        
        results = notification_service.send_notification(
            message=request.message,
            title=request.title,
            methods=methods
        )
        
        return {
            "message": "Notification sent",
            "results": results,
            "success_count": sum(1 for success in results.values() if success),
            "total_methods": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notifications/test")
def test_notifications():
    """Test all configured notification methods"""
    if notification_service is None:
        raise HTTPException(status_code=503, detail="Notification service not available")
    
    try:
        results = notification_service.test_notifications()
        return {
            "message": "Notification test completed",
            "results": results,
            "success_count": sum(1 for success in results.values() if success),
            "total_methods": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/notifications/sms-gmail")
def send_sms_via_gmail(phone_number: str, carrier: str, message: str):
    """Send SMS via Gmail API using existing authentication (no passwords needed!)"""
    if gmail_service is None:
        raise HTTPException(status_code=503, detail="Gmail service not available")
    
    try:
        success = gmail_service.send_sms_notification(
            phone_number=phone_number,
            carrier=carrier,
            message=message
        )
        
        # Get the SMS gateway address for display
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
        
        return {
            "message": "SMS sent successfully via Gmail!" if success else "Failed to send SMS via Gmail",
            "success": success,
            "sms_address": f"{phone_number}{sms_gateways.get(carrier.lower(), '@unknown')}",
            "method": "Gmail API (no passwords needed)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications/carriers")
def get_supported_carriers():
    """Get list of supported SMS carriers"""
    if notification_service is None:
        raise HTTPException(status_code=503, detail="Notification service not available")
    
    return {
        "carriers": notification_service.SMS_GATEWAYS,
        "example_usage": {
            "phone_number": "1234567890",
            "carrier": "att",
            "sms_address": "1234567890@txt.att.net"
        }
    }

@app.post("/notifications/quick")
def send_quick_notification_endpoint(message: str, title: str = "Alert"):
    """Quick notification using environment variables"""
    try:
        result = send_quick_notification(message, title)
        return {
            "message": "Quick notification sent",
            "results": result,
            "success_count": sum(1 for success in result.values() if success),
            "total_methods": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

