import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from .memory_types import MemoryEntry, MemoryType, MemoryQuery


class ChromaMemoryManager:
    """Manages vector-based memory storage using ChromaDB"""
    
    def __init__(self, collection_name="aut_agent_memories"):
        """
        Initialize the ChromaDB memory manager
        
        Args:
            collection_name: Name of the ChromaDB collection
        """
        # Connect to ChromaDB server running in Docker
        self.client = chromadb.HttpClient(host="chroma", port=8000)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def add_memory(self, content: str, memory_type: MemoryType, 
                   metadata: Optional[Dict[str, Any]] = None,
                   importance_score: Optional[float] = None) -> str:
        """
        Add a new memory entry
        
        Args:
            content: The memory content
            memory_type: Type of memory
            metadata: Additional metadata
            importance_score: Importance score (0-1)
            
        Returns:
            Memory ID
        """
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Generate embedding
        embedding = self.embeddings.embed_query(content)
        
        # Prepare metadata for ChromaDB
        chroma_metadata = {
            "memory_type": memory_type.value,
            "timestamp": timestamp.isoformat(),
            "importance_score": importance_score or 0.5
        }
        
        if metadata:
            chroma_metadata.update(metadata)
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[chroma_metadata],
            ids=[memory_id]
        )
        
        return memory_id
    
    def search_memories(self, query: str, memory_type: Optional[MemoryType] = None,
                       limit: int = 10, similarity_threshold: float = 0.7) -> List[MemoryEntry]:
        """
        Search for relevant memories
        
        Args:
            query: Search query
            memory_type: Filter by memory type
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of relevant memory entries
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Prepare where clause for filtering
        where_clause = {}
        if memory_type:
            where_clause["memory_type"] = memory_type.value
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=where_clause if where_clause else None
        )
        
        # Convert to MemoryEntry objects
        memories = []
        if results['ids'] and results['ids'][0]:
            for i, memory_id in enumerate(results['ids'][0]):
                if results['distances'][0][i] <= (1 - similarity_threshold):  # Convert similarity to distance
                    metadata = results['metadatas'][0][i]
                    memory = MemoryEntry(
                        id=memory_id,
                        content=results['documents'][0][i],
                        memory_type=MemoryType(metadata['memory_type']),
                        timestamp=datetime.fromisoformat(metadata['timestamp']),
                        metadata={k: v for k, v in metadata.items() 
                                if k not in ['memory_type', 'timestamp', 'importance_score']},
                        importance_score=metadata.get('importance_score', 0.5)
                    )
                    memories.append(memory)
        
        return memories
    
    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific memory by ID"""
        try:
            result = self.collection.get(ids=[memory_id])
            if result['ids']:
                metadata = result['metadatas'][0]
                return MemoryEntry(
                    id=memory_id,
                    content=result['documents'][0],
                    memory_type=MemoryType(metadata['memory_type']),
                    timestamp=datetime.fromisoformat(metadata['timestamp']),
                    metadata={k: v for k, v in metadata.items() 
                            if k not in ['memory_type', 'timestamp', 'importance_score']},
                    importance_score=metadata.get('importance_score', 0.5)
                )
        except Exception:
            return None
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID"""
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False
    
    def get_memories_by_type(self, memory_type: MemoryType, limit: int = 100) -> List[MemoryEntry]:
        """Get all memories of a specific type"""
        results = self.collection.get(
            where={"memory_type": memory_type.value},
            limit=limit
        )
        
        memories = []
        for i, memory_id in enumerate(results['ids']):
            metadata = results['metadatas'][i]
            memory = MemoryEntry(
                id=memory_id,
                content=results['documents'][i],
                memory_type=MemoryType(metadata['memory_type']),
                timestamp=datetime.fromisoformat(metadata['timestamp']),
                metadata={k: v for k, v in metadata.items() 
                        if k not in ['memory_type', 'timestamp', 'importance_score']},
                importance_score=metadata.get('importance_score', 0.5)
            )
            memories.append(memory)
        
        return memories
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        try:
            count = self.collection.count()
            
            # Get all memories to analyze
            all_memories = self.collection.get(limit=10000)
            
            # Count by type
            type_counts = {}
            if all_memories['metadatas']:
                for metadata in all_memories['metadatas']:
                    memory_type = metadata['memory_type']
                    type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
            
            return {
                "total_memories": count,
                "memories_by_type": type_counts,
                "collection_name": self.collection.name
            }
        except Exception as e:
            return {"error": str(e)}
    
    def clear_all_memories(self) -> bool:
        """Clear all memories from the collection"""
        try:
            print(f"Clearing all memories from collection: {self.collection.name}")
            
            # Get all document IDs first
            all_docs = self.collection.get(limit=10000)
            print(f"Found {len(all_docs['ids'])} documents to delete")
            
            if all_docs['ids']:
                # Delete all documents by their IDs
                self.collection.delete(ids=all_docs['ids'])
                print(f"Deleted {len(all_docs['ids'])} documents")
                
                # Verify deletion
                remaining = self.collection.count()
                print(f"Remaining documents after deletion: {remaining}")
                
                if remaining > 0:
                    print("Warning: Some documents may still remain")
                    return False
                else:
                    print("All documents successfully deleted")
                    return True
            else:
                print("No documents found to delete")
                return True
                
        except Exception as e:
            print(f"Error clearing memories: {e}")
            return False
    
    def clear_all_memories_detailed(self) -> Dict[str, Any]:
        """Clear all memories from the collection and return detailed information"""
        try:
            print(f"Clearing all memories from collection: {self.collection.name}")
            
            # Get all document IDs first
            all_docs = self.collection.get(limit=10000)
            documents_found = len(all_docs['ids'])
            print(f"Found {documents_found} documents to delete")
            
            if all_docs['ids']:
                # Delete all documents by their IDs
                self.collection.delete(ids=all_docs['ids'])
                print(f"Deleted {documents_found} documents")
                
                # Verify deletion
                remaining = self.collection.count()
                print(f"Remaining documents after deletion: {remaining}")
                
                if remaining > 0:
                    print("Warning: Some documents may still remain")
                    return {
                        "success": False,
                        "documents_found": documents_found,
                        "documents_deleted": documents_found,
                        "documents_remaining": remaining,
                        "message": "Some documents may still remain after deletion",
                        "collection_name": self.collection.name
                    }
                else:
                    print("All documents successfully deleted")
                    return {
                        "success": True,
                        "documents_found": documents_found,
                        "documents_deleted": documents_found,
                        "documents_remaining": 0,
                        "message": "All documents successfully deleted",
                        "collection_name": self.collection.name
                    }
            else:
                print("No documents found to delete")
                return {
                    "success": True,
                    "documents_found": 0,
                    "documents_deleted": 0,
                    "documents_remaining": 0,
                    "message": "No documents found to delete",
                    "collection_name": self.collection.name
                }
                
        except Exception as e:
            error_msg = f"Error clearing memories: {e}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "collection_name": self.collection.name
            } 