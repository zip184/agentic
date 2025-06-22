import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from memory import ChromaMemoryManager, MemoryType, MemoryEntry

load_dotenv()


class MemoryAwareAgent:
    """An agent that uses ChromaDB for persistent memory"""
    
    def __init__(self, memory_manager: Optional[ChromaMemoryManager] = None):
        """
        Initialize the memory-aware agent
        
        Args:
            memory_manager: ChromaDB memory manager instance
        """
        self.llm = OpenAI(temperature=0.7, openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.memory_manager = memory_manager or ChromaMemoryManager()
        
        # Enhanced prompt template that includes memory context
        self.prompt_template = PromptTemplate(
            input_variables=["goal", "relevant_memories", "current_context"],
            template="""
You are an autonomous agent with access to a memory system. Use the relevant memories to inform your decisions.

Current Goal: {goal}

Relevant Memories from Past Experiences:
{relevant_memories}

Current Context: {current_context}

Based on your goal and the relevant memories, provide a thoughtful response or action plan.
Consider what you've learned from past experiences and how it applies to the current situation.
"""
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
    
    def run_agent(self, goal: str, current_context: str = "", 
                  memory_search_limit: int = 5) -> str:
        """
        Run the agent with memory-enhanced decision making
        
        Args:
            goal: The current goal
            current_context: Additional context about the current situation
            memory_search_limit: Number of relevant memories to retrieve
            
        Returns:
            Agent's response
        """
        # Search for relevant memories
        relevant_memories = self._get_relevant_memories(goal, memory_search_limit)
        
        # Format memories for the prompt
        memories_text = self._format_memories(relevant_memories)

        print(f"Memories text: {memories_text}")
        
        # Run the agent with memory context
        response = self.chain.run({
            "goal": goal,
            "relevant_memories": memories_text,
            "current_context": current_context
        })
        
        # Store this interaction as a memory
        self._store_interaction(goal, response, current_context)
        
        return response
    
    def _get_relevant_memories(self, query: str, limit: int = 5) -> List[MemoryEntry]:
        """Retrieve relevant memories for a given query"""
        return self.memory_manager.search_memories(
            query=query,
            limit=limit,
            similarity_threshold=0.3
        )
    
    def _format_memories(self, memories: List[MemoryEntry]) -> str:
        """Format memories for inclusion in the prompt"""
        if not memories:
            return "No relevant memories found."
        
        formatted_memories = []
        for memory in memories:
            formatted_memories.append(
                f"- [{memory.memory_type.value}] {memory.content} "
                f"(Importance: {memory.importance_score:.2f})"
            )
        
        return "\n".join(formatted_memories)
    
    def _store_interaction(self, goal: str, response: str, context: str = ""):
        """Store the current interaction as a memory"""
        # Store the goal
        self.memory_manager.add_memory(
            content=goal,
            memory_type=MemoryType.GOAL,
            metadata={"context": context}
        )
        
        # Store the response as an action
        self.memory_manager.add_memory(
            content=response,
            memory_type=MemoryType.ACTION,
            metadata={"goal": goal, "context": context}
        )
    
    def add_observation(self, observation: str, importance_score: float = 0.5,
                       metadata: Optional[Dict[str, Any]] = None):
        """Add an observation to memory"""
        self.memory_manager.add_memory(
            content=observation,
            memory_type=MemoryType.OBSERVATION,
            importance_score=importance_score,
            metadata=metadata
        )
    
    def add_learning(self, learning: str, importance_score: float = 0.8,
                    metadata: Optional[Dict[str, Any]] = None):
        """Add a learning/insight to memory"""
        self.memory_manager.add_memory(
            content=learning,
            memory_type=MemoryType.LEARNING,
            importance_score=importance_score,
            metadata=metadata
        )
    
    def add_reflection(self, reflection: str, importance_score: float = 0.7,
                      metadata: Optional[Dict[str, Any]] = None):
        """Add a reflection to memory"""
        self.memory_manager.add_memory(
            content=reflection,
            memory_type=MemoryType.REFLECTION,
            importance_score=importance_score,
            metadata=metadata
        )
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the agent's memory"""
        return self.memory_manager.get_memory_stats()
    
    def search_memories(self, query: str, memory_type: Optional[MemoryType] = None,
                       limit: int = 10) -> List[MemoryEntry]:
        """Search memories with optional type filtering"""
        return self.memory_manager.search_memories(
            query=query,
            memory_type=memory_type,
            limit=limit
        )
    
    def get_memories_by_type(self, memory_type: MemoryType, limit: int = 100) -> List[MemoryEntry]:
        """Get all memories of a specific type"""
        return self.memory_manager.get_memories_by_type(memory_type, limit) 