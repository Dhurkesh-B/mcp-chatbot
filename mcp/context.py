from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from .protocol import ContextItem, MCPProtocol

class ContextManager:
    """Manages context for the MCP implementation."""
    
    def __init__(self, mcp_protocol: MCPProtocol):
        self.mcp = mcp_protocol

    def add_github_context(self, github_data: Dict[str, Any]) -> str:
        """Add GitHub data to the context."""
        item = ContextItem(
            id=str(uuid.uuid4()),
            type="github",
            content=github_data,
            metadata={
                "source": "github_api",
                "data_type": "repository_info"
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="github",
            relevance_score=0.8
        )
        self.mcp.add_context_item(item)
        return item.id

    def add_rag_context(self, rag_data: Dict[str, Any]) -> str:
        """Add RAG data to the context."""
        item = ContextItem(
            id=str(uuid.uuid4()),
            type="rag",
            content=rag_data,
            metadata={
                "source": "local_content",
                "data_type": "rag_search"
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="rag",
            relevance_score=0.9
        )
        self.mcp.add_context_item(item)
        return item.id

    def add_user_message(self, message: str) -> str:
        """Add a user message to the context."""
        item = ContextItem(
            id=str(uuid.uuid4()),
            type="user_message",
            content=message,
            metadata={
                "source": "user_input",
                "data_type": "message"
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="user",
            relevance_score=1.0
        )
        self.mcp.add_context_item(item)
        return item.id

    def add_assistant_message(self, message: str) -> str:
        """Add an assistant message to the context."""
        item = ContextItem(
            id=str(uuid.uuid4()),
            type="assistant_message",
            content=message,
            metadata={
                "source": "assistant",
                "data_type": "message"
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            source="assistant",
            relevance_score=0.7
        )
        self.mcp.add_context_item(item)
        return item.id

    def get_conversation_context(self, limit: int = 10) -> List[ContextItem]:
        """Get the recent conversation context."""
        messages = self.mcp.get_context_items(type="user_message") + \
                  self.mcp.get_context_items(type="assistant_message")
        messages.sort(key=lambda x: x.created_at, reverse=True)
        return messages[:limit]

    def get_relevant_context_for_query(self, query: str) -> Dict[str, Any]:
        """Get all relevant context for a given query."""
        # Get relevant context items
        relevant_items = self.mcp.get_relevant_context(query)
        
        # Organize context by type
        context = {
            "github": [],
            "rag": [],
            "conversation": []
        }
        
        for item in relevant_items:
            if item.type == "github":
                context["github"].append(item.content)
            elif item.type == "rag":
                context["rag"].append(item.content)
            elif item.type in ["user_message", "assistant_message"]:
                context["conversation"].append(item.content)
        
        return context

    def update_relevance_scores(self, query: str) -> None:
        """Update relevance scores based on the current query."""
        for item in self.mcp.context.items:
            # Simple relevance scoring based on content matching
            if isinstance(item.content, str) and query.lower() in item.content.lower():
                item.relevance_score = min(1.0, item.relevance_score + 0.2)
            else:
                item.relevance_score = max(0.0, item.relevance_score - 0.1)