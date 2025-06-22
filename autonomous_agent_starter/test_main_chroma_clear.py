#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to clear the main ChromaDB directory used by the API.
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from memory import ChromaMemoryManager, MemoryType

load_dotenv()


def test_main_chroma_clear():
    """Test clearing the main ChromaDB directory"""
    print("🧪 Testing Main ChromaDB Clear...")
    
    # Initialize memory manager with the SAME directory as the API
    memory_manager = ChromaMemoryManager(
        persist_directory="./chroma_db",  # Same as API
        collection_name="agent_memories"  # Same as API
    )
    
    # Check current count
    stats_before = memory_manager.get_memory_stats()
    print(f"  📊 Memories before clear: {stats_before['total_memories']}")
    print(f"  📊 Memory types: {stats_before.get('memories_by_type', {})}")
    
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
        print("✅ Main ChromaDB clear test PASSED!")
        return True
    else:
        print("❌ Main ChromaDB clear test FAILED!")
        print(f"   Expected 0 memories, got {stats_after['total_memories']}")
        print(f"   Expected 0 search results, got {len(search_results)}")
        return False


if __name__ == "__main__":
    success = test_main_chroma_clear()
    exit(0 if success else 1) 