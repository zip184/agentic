#!/usr/bin/env python3
"""
Scheduler Service

Provides API-controlled scheduling for Nintendo monitoring and other tasks.
Uses APScheduler for job management.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobConfig:
    """Configuration for a scheduled job"""
    id: str
    name: str
    description: str
    endpoint: str
    schedule_type: str  # 'interval' or 'cron'
    schedule_value: str  # '15' for 15 minutes, or '*/15 * * * *' for cron
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    run_count: int = 0

class SchedulerService:
    """Service for managing scheduled jobs"""
    
    def __init__(self, gmail_service=None, nintendo_monitor=None):
        self.gmail_service = gmail_service
        self.nintendo_monitor = nintendo_monitor
        
        # Configure APScheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        self.jobs: Dict[str, JobConfig] = {}
        self.is_running = False
        
    def start_scheduler(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler started successfully")
        else:
            logger.warning("Scheduler is already running")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped successfully")
        else:
            logger.warning("Scheduler is not running")
    
    def add_job(self, job_config: JobConfig) -> bool:
        """Add a new scheduled job"""
        try:
            # Remove existing job if it exists
            if job_config.id in self.jobs:
                self.remove_job(job_config.id)
            
            # Create trigger based on schedule type
            if job_config.schedule_type == 'interval':
                trigger = IntervalTrigger(minutes=int(job_config.schedule_value))
            elif job_config.schedule_type == 'cron':
                # Parse cron expression
                parts = job_config.schedule_value.split()
                if len(parts) == 5:
                    minute, hour, day, month, day_of_week = parts
                    trigger = CronTrigger(
                        minute=minute,
                        hour=hour, 
                        day=day,
                        month=month,
                        day_of_week=day_of_week
                    )
                else:
                    raise ValueError(f"Invalid cron expression: {job_config.schedule_value}")
            else:
                raise ValueError(f"Unknown schedule type: {job_config.schedule_type}")
            
            # Add job to scheduler
            self.scheduler.add_job(
                func=self._execute_job,
                trigger=trigger,
                id=job_config.id,
                name=job_config.name,
                args=[job_config.id],
                replace_existing=True
            )
            
            # Store job config
            self.jobs[job_config.id] = job_config
            logger.info(f"Added job '{job_config.name}' with ID '{job_config.id}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add job '{job_config.id}': {e}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """Remove a scheduled job"""
        try:
            if job_id in self.jobs:
                self.scheduler.remove_job(job_id)
                del self.jobs[job_id]
                logger.info(f"Removed job with ID '{job_id}'")
                return True
            else:
                logger.warning(f"Job with ID '{job_id}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove job '{job_id}': {e}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job"""
        try:
            if job_id in self.jobs:
                self.scheduler.pause_job(job_id)
                self.jobs[job_id].enabled = False
                logger.info(f"Paused job with ID '{job_id}'")
                return True
            else:
                logger.warning(f"Job with ID '{job_id}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to pause job '{job_id}': {e}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job"""
        try:
            if job_id in self.jobs:
                self.scheduler.resume_job(job_id)
                self.jobs[job_id].enabled = True
                logger.info(f"Resumed job with ID '{job_id}'")
                return True
            else:
                logger.warning(f"Job with ID '{job_id}' not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to resume job '{job_id}': {e}")
            return False
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        if job_id in self.jobs:
            job_config = self.jobs[job_id]
            scheduler_job = self.scheduler.get_job(job_id)
            
            if scheduler_job:
                job_config.next_run = scheduler_job.next_run_time.isoformat() if scheduler_job.next_run_time else None
            
            return asdict(job_config)
        return None
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get status of all jobs"""
        job_list = []
        for job_id in self.jobs:
            job_status = self.get_job_status(job_id)
            if job_status:
                job_list.append(job_status)
        return job_list
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get overall scheduler status"""
        return {
            "running": self.is_running,
            "total_jobs": len(self.jobs),
            "active_jobs": len([j for j in self.jobs.values() if j.enabled]),
            "paused_jobs": len([j for j in self.jobs.values() if not j.enabled])
        }
    
    async def _execute_job(self, job_id: str):
        """Execute a scheduled job"""
        if job_id not in self.jobs:
            logger.error(f"Job '{job_id}' not found during execution")
            return
        
        job_config = self.jobs[job_id]
        logger.info(f"Executing job '{job_config.name}' (ID: {job_id})")
        
        try:
            # Update job stats
            job_config.last_run = datetime.now().isoformat()
            job_config.run_count += 1
            
            # Execute based on endpoint
            if job_config.endpoint == 'nintendo_monitor':
                if self.nintendo_monitor:
                    await self.nintendo_monitor._check_for_switch2_emails()
                    logger.info(f"Nintendo monitor job completed successfully")
                else:
                    logger.error("Nintendo monitor not available")
            else:
                logger.warning(f"Unknown endpoint: {job_config.endpoint}")
                
        except Exception as e:
            logger.error(f"Error executing job '{job_id}': {e}")
    
    def add_nintendo_monitor_job(self, interval_minutes: int = 15) -> bool:
        """Convenience method to add Nintendo monitoring job"""
        job_config = JobConfig(
            id="nintendo_monitor",
            name="Nintendo Switch 2 Monitor",
            description="Monitor Gmail for Nintendo Switch 2 emails and send alerts",
            endpoint="nintendo_monitor",
            schedule_type="interval",
            schedule_value=str(interval_minutes),
            enabled=True
        )
        
        return self.add_job(job_config)
    
    def add_nintendo_monitor_cron(self, cron_expression: str = "*/15 * * * *") -> bool:
        """Convenience method to add Nintendo monitoring with cron schedule"""
        job_config = JobConfig(
            id="nintendo_monitor_cron",
            name="Nintendo Switch 2 Monitor (Cron)",
            description="Monitor Gmail for Nintendo Switch 2 emails using cron schedule",
            endpoint="nintendo_monitor",
            schedule_type="cron",
            schedule_value=cron_expression,
            enabled=True
        )
        
        return self.add_job(job_config) 