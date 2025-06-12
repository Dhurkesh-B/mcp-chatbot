from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from .protocol import MemoryItem, MCPProtocol

class MemoryManager:
    """Manages memory for the MCP implementation."""
    
    def __init__(self, mcp_protocol: MCPProtocol):
        self.mcp = mcp_protocol

    def add_important_fact(self, fact: str, importance: float = 0.8) -> str:
        """Add an important fact to memory."""
        item = MemoryItem(
            id=str(uuid.uuid4()),
            type="fact",
            content=fact,
            metadata={
                "source": "user_interaction",
                "data_type": "fact"
            },
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            importance_score=importance
        )
        self.mcp.add_memory_item(item)
        return item.id

    def add_user_preference(self, preference: Dict[str, Any]) -> str:
        """Add a user preference to memory."""
        item = MemoryItem(
            id=str(uuid.uuid4()),
            type="preference",
            content=preference,
            metadata={
                "source": "user_interaction",
                "data_type": "preference"
            },
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            importance_score=0.9
        )
        self.mcp.add_memory_item(item)
        return item.id

    def add_interaction_pattern(self, pattern: Dict[str, Any]) -> str:
        """Add an interaction pattern to memory."""
        item = MemoryItem(
            id=str(uuid.uuid4()),
            type="pattern",
            content=pattern,
            metadata={
                "source": "user_interaction",
                "data_type": "pattern"
            },
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            importance_score=0.7
        )
        self.mcp.add_memory_item(item)
        return item.id

    def get_relevant_memories(self, query: str) -> List[MemoryItem]:
        """Get memories relevant to the current query."""
        memories = self.mcp.get_memory_items()
        relevant_memories = []
        
        for memory in memories:
            # Simple relevance check based on content matching
            if isinstance(memory.content, str) and query.lower() in memory.content.lower():
                relevant_memories.append(memory)
            elif isinstance(memory.content, dict):
                # Check dictionary values for matches
                for value in memory.content.values():
                    if isinstance(value, str) and query.lower() in value.lower():
                        relevant_memories.append(memory)
                        break
        
        return relevant_memories

    def update_memory_importance(self, memory_id: str, new_importance: float) -> bool:
        """Update the importance score of a memory item."""
        return self.mcp.update_memory_item(memory_id, {"importance_score": new_importance})

    def get_important_memories(self, limit: int = 5) -> List[MemoryItem]:
        """Get the most important memories."""
        return self.mcp.get_important_memories(limit)

    def forget_old_memories(self, days_threshold: int = 30) -> int:
        """Remove memories older than the threshold."""
        current_time = datetime.now()
        memories_to_keep = []
        forgotten_count = 0
        
        for memory in self.mcp.memory.items:
            age_days = (current_time - memory.created_at).days
            if age_days <= days_threshold or memory.importance_score > 0.8:
                memories_to_keep.append(memory)
            else:
                forgotten_count += 1
        
        self.mcp.memory.items = memories_to_keep
        return forgotten_count