#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify memory clearing functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory import ChromaMemoryManager, MemoryType

load_dotenv()


def test_memory_clear():
    """Test that memory clearing actually works"""
    print("🧪 Testing Memory Clear Functionality...")
    
    # Initialize memory manager with a test collection
    memory_manager = ChromaMemoryManager(
        persist_directory="./test_clear_chroma_db",
        collection_name="test_memories"
    )
    
    # Add some test memories
    print("  📝 Adding test memories...")
    memory_manager.add_memory(
        content="Test memory 1: My favorite color is blue",
        memory_type=MemoryType.OBSERVATION,
        importance_score=0.8
    )
    memory_manager.add_memory(
        content="Test memory 2: I like pizza",
        memory_type=MemoryType.OBSERVATION,
        importance_score=0.7
    )
    memory_manager.add_memory(
        content="Test memory 3: I work as a developer",
        memory_type=MemoryType.OBSERVATION,
        importance_score=0.9
    )
    
    # Check initial count
    stats_before = memory_manager.get_memory_stats()
    print(f"  📊 Memories before clear: {stats_before['total_memories']}")
    
    # Clear all memories
    print("  🧹 Clearing all memories...")
    success = memory_manager.clear_all_memories()
    print(f"  ✅ Clear operation success: {success}")
    
    # Check count after clear
    stats_after = memory_manager.get_memory_stats()
    print(f"  📊 Memories after clear: {stats_after['total_memories']}")
    
    # Test search after clear
    print("  🔍 Testing search after clear...")
    search_results = memory_manager.search_memories("blue", limit=5)
    print(f"  📊 Search results after clear: {len(search_results)}")
    
    if stats_after['total_memories'] == 0 and len(search_results) == 0:
        print("✅ Memory clear test PASSED!")
        return True
    else:
        print("❌ Memory clear test FAILED!")
        print(f"   Expected 0 memories, got {stats_after['total_memories']}")
        print(f"   Expected 0 search results, got {len(search_results)}")
        return False


if __name__ == "__main__":
    success = test_memory_clear()
    exit(0 if success else 1) 