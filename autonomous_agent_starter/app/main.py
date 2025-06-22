from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from agents.agent import run_agent
from agents.memory_agent import MemoryAwareAgent
from memory import MemoryType, ChromaMemoryManager

app = FastAPI(title="Autonomous Agent API with Memory", version="1.0.0")

# Initialize the memory-aware agent
memory_agent = MemoryAwareAgent()

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

