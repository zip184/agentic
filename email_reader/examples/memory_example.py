#!/usr/bin/env python3
"""
Example script demonstrating ChromaDB memory integration with the autonomous agent.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.memory_agent import MemoryAwareAgent
from memory import MemoryType

load_dotenv()


def main():
    """Demonstrate the memory-aware agent capabilities"""
    
    print("🤖 Initializing Memory-Aware Agent...")
    
    # Initialize the memory-aware agent
    agent = MemoryAwareAgent()
    
    # Add some initial memories to demonstrate the system
    print("\n📝 Adding some initial memories...")
    
    # Add some observations
    agent.add_observation(
        "Users prefer simple, clear interfaces over complex ones",
        importance_score=0.8,
        metadata={"domain": "UI/UX", "source": "user_feedback"}
    )
    
    agent.add_observation(
        "Database queries are slow when there are no indexes",
        importance_score=0.9,
        metadata={"domain": "performance", "source": "monitoring"}
    )
    
    # Add some learnings
    agent.add_learning(
        "Breaking down complex tasks into smaller steps improves success rate",
        importance_score=0.9,
        metadata={"domain": "productivity", "source": "experience"}
    )
    
    agent.add_learning(
        "Regular backups prevent data loss in critical situations",
        importance_score=0.95,
        metadata={"domain": "data_management", "source": "incident_response"}
    )
    
    # Add some reflections
    agent.add_reflection(
        "I should always consider the user's perspective when making decisions",
        importance_score=0.8,
        metadata={"domain": "decision_making", "source": "self_reflection"}
    )
    
    print("✅ Initial memories added!")
    
    # Demonstrate memory-enhanced decision making
    print("\n🧠 Testing memory-enhanced decision making...")
    
    # Test 1: UI/UX related goal
    print("\n--- Test 1: UI/UX Goal ---")
    response1 = agent.run_agent(
        goal="Design a new user interface for a mobile app",
        current_context="The app needs to be intuitive for elderly users",
        memory_search_limit=3
    )
    print(f"Goal: Design a new user interface for a mobile app")
    print(f"Response: {response1}")
    
    # Test 2: Performance related goal
    print("\n--- Test 2: Performance Goal ---")
    response2 = agent.run_agent(
        goal="Optimize database performance for a web application",
        current_context="The application is experiencing slow response times",
        memory_search_limit=3
    )
    print(f"Goal: Optimize database performance for a web application")
    print(f"Response: {response2}")
    
    # Test 3: General problem-solving goal
    print("\n--- Test 3: Problem-Solving Goal ---")
    response3 = agent.run_agent(
        goal="Plan a complex software development project",
        current_context="The project involves multiple teams and tight deadlines",
        memory_search_limit=3
    )
    print(f"Goal: Plan a complex software development project")
    print(f"Response: {response3}")
    
    # Demonstrate memory search capabilities
    print("\n🔍 Demonstrating memory search capabilities...")
    
    # Search for performance-related memories
    performance_memories = agent.search_memories("performance optimization", limit=5)
    print(f"\nFound {len(performance_memories)} performance-related memories:")
    for memory in performance_memories:
        print(f"  - [{memory.memory_type.value}] {memory.content}")
    
    # Get all learnings
    learnings = agent.get_memories_by_type(MemoryType.LEARNING, limit=10)
    print(f"\nFound {len(learnings)} learning memories:")
    for learning in learnings:
        print(f"  - {learning.content}")
    
    # Show memory statistics
    print("\n📊 Memory Statistics:")
    stats = agent.get_memory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Memory system demonstration complete!")


if __name__ == "__main__":
    main() 