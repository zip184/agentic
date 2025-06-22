#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script to verify the ChromaDB memory system is working.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory import ChromaMemoryManager, MemoryType
from agents.memory_agent import MemoryAwareAgent

load_dotenv()


def test_memory_manager():
    """Test the basic memory manager functionality"""
    print("🧪 Testing ChromaMemoryManager...")
    
    # Initialize memory manager
    memory_manager = ChromaMemoryManager(persist_directory="./test_chroma_db")
    
    # Test adding memories
    print("  📝 Adding test memories...")
    
    memory_id1 = memory_manager.add_memory(
        content="Test observation: Users prefer simple interfaces",
        memory_type=MemoryType.OBSERVATION,
        importance_score=0.8
    )
    
    memory_id2 = memory_manager.add_memory(
        content="Test learning: Breaking tasks into steps improves success",
        memory_type=MemoryType.LEARNING,
        importance_score=0.9
    )
    
    print(f"  ✅ Added memories with IDs: {memory_id1}, {memory_id2}")
    
    # Test searching memories
    print("  🔍 Testing memory search...")
    search_results = memory_manager.search_memories("user interface", limit=5)
    print(f"  ✅ Found {len(search_results)} relevant memories")
    
    # Test getting memories by type
    print("  📊 Testing memory retrieval by type...")
    observations = memory_manager.get_memories_by_type(MemoryType.OBSERVATION, limit=10)
    learnings = memory_manager.get_memories_by_type(MemoryType.LEARNING, limit=10)
    print(f"  ✅ Found {len(observations)} observations and {len(learnings)} learnings")
    
    # Test memory stats
    print("  📈 Testing memory statistics...")
    stats = memory_manager.get_memory_stats()
    print(f"  ✅ Memory stats: {stats}")
    
    # Clean up
    print("  🧹 Cleaning up test data...")
    memory_manager.delete_memory(memory_id1)
    memory_manager.delete_memory(memory_id2)
    
    print("✅ ChromaMemoryManager tests passed!")


def test_memory_agent():
    """Test the memory-aware agent"""
    print("\n🤖 Testing MemoryAwareAgent...")
    
    # Initialize agent
    agent = MemoryAwareAgent()
    
    # Add some test memories
    print("  📝 Adding test memories to agent...")
    agent.add_observation("Users prefer large buttons and clear text", importance_score=0.8)
    agent.add_learning("Testing early prevents bugs later", importance_score=0.9)
    agent.add_reflection("Always consider accessibility in design", importance_score=0.7)
    
    # Test running agent with memory
    print("  🧠 Testing memory-enhanced decision making...")
    response = agent.run_agent(
        goal="Design a mobile app for elderly users",
        current_context="Need to ensure accessibility",
        memory_search_limit=3
    )
    
    print(f"  ✅ Agent response: {response[:100]}...")
    
    # Test memory search
    print("  🔍 Testing agent memory search...")
    memories = agent.search_memories("user interface design", limit=5)
    print(f"  ✅ Found {len(memories)} relevant memories")
    
    print("✅ MemoryAwareAgent tests passed!")


def main():
    """Run all tests"""
    print("🚀 Starting ChromaDB Memory System Tests...\n")
    
    try:
        # Check if OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠️  Warning: OPENAI_API_KEY not set. Some tests may fail.")
            print("   Set it in your .env file or environment variables.\n")
        
        # Run tests
        test_memory_manager()
        test_memory_agent()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📚 Next steps:")
        print("   1. Run 'python examples/memory_example.py' for a full demonstration")
        print("   2. Start the API with 'uvicorn app.main:app --reload'")
        print("   3. Check the README.md for detailed usage instructions")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("   Make sure you have:")
        print("   1. Installed all dependencies: pip install -r requirements.txt")
        print("   2. Set your OPENAI_API_KEY in .env file")
        print("   3. Have an active internet connection for OpenAI API calls")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 