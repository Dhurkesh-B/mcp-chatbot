from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class ContextItem(BaseModel):
    """Represents a single context item in the MCP protocol."""
    id: str
    type: str
    content: Any
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    source: str
    relevance_score: float = 0.0

class MemoryItem(BaseModel):
    """Represents a memory item in the MCP protocol."""
    id: str
    type: str
    content: Any
    metadata: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    importance_score: float = 0.0

class Context(BaseModel):
    """Represents the complete context in the MCP protocol."""
    items: List[ContextItem]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0"

class Memory(BaseModel):
    """Represents the memory store in the MCP protocol."""
    items: List[MemoryItem]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0"

class MCPProtocol:
    """Implementation of the Model Context Protocol."""
    
    def __init__(self):
        self.context = Context(
            items=[],
            metadata={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.memory = Memory(
            items=[],
            metadata={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    def add_context_item(self, item: ContextItem) -> None:
        """Add a new context item."""
        self.context.items.append(item)
        self.context.updated_at = datetime.now()

    def get_context_items(self, type: Optional[str] = None) -> List[ContextItem]:
        """Get context items, optionally filtered by type."""
        if type:
            return [item for item in self.context.items if item.type == type]
        return self.context.items

    def update_context_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing context item."""
        for item in self.context.items:
            if item.id == item_id:
                for key, value in updates.items():
                    setattr(item, key, value)
                item.updated_at = datetime.now()
                self.context.updated_at = datetime.now()
                return True
        return False

    def add_memory_item(self, item: MemoryItem) -> None:
        """Add a new memory item."""
        self.memory.items.append(item)
        self.memory.updated_at = datetime.now()

    def get_memory_items(self, type: Optional[str] = None) -> List[MemoryItem]:
        """Get memory items, optionally filtered by type."""
        if type:
            return [item for item in self.memory.items if item.type == type]
        return self.memory.items

    def update_memory_item(self, item_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory item."""
        for item in self.memory.items:
            if item.id == item_id:
                for key, value in updates.items():
                    setattr(item, key, value)
                item.last_accessed = datetime.now()
                item.access_count += 1
                self.memory.updated_at = datetime.now()
                return True
        return False

    def get_relevant_context(self, query: str, limit: int = 5) -> List[ContextItem]:
        """Get the most relevant context items for a given query."""
        # Sort items by relevance score and return top N
        sorted_items = sorted(
            self.context.items,
            key=lambda x: x.relevance_score,
            reverse=True
        )
        return sorted_items[:limit]

    def get_important_memories(self, limit: int = 5) -> List[MemoryItem]:
        """Get the most important memory items."""
        # Sort items by importance score and return top N
        sorted_items = sorted(
            self.memory.items,
            key=lambda x: x.importance_score,
            reverse=True
        )
        return sorted_items[:limit]