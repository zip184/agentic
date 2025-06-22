from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class MemoryType(str, Enum):
    """Types of memories that can be stored"""
    OBSERVATION = "observation"
    ACTION = "action"
    GOAL = "goal"
    REFLECTION = "reflection"
    LEARNING = "learning"
    CONTEXT = "context"


class MemoryEntry(BaseModel):
    """Represents a single memory entry"""
    id: str
    content: str
    memory_type: MemoryType
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    embedding: Optional[list] = None
    importance_score: Optional[float] = None
    
    class Config:
        arbitrary_types_allowed = True


class MemoryQuery(BaseModel):
    """Query parameters for searching memories"""
    query: str
    memory_type: Optional[MemoryType] = None
    limit: int = 10
    similarity_threshold: float = 0.7
    time_filter: Optional[Dict[str, datetime]] = None 