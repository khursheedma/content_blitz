"""Conversation memory management."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.vector_db import VectorMemory
import uuid


class ConversationMemory:
    """Manages conversation context and history."""

    def __init__(self):
        """Initialize conversation memory."""
        self.vector_memory = VectorMemory()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, brand_info: Optional[Dict[str, Any]] = None) -> str:
        """Create a new conversation session.

        Args:
            brand_info: Brand information for the session

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        self.active_sessions[session_id] = {
            "created_at": datetime.utcnow().isoformat(),
            "brand_info": brand_info or {},
            "message_count": 0,
            "last_activity": datetime.utcnow().isoformat()
        }

        return session_id

    def add_message(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        agent_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a message exchange to session memory.

        Args:
            session_id: Session identifier
            user_message: User's message
            agent_response: Agent's response
            agent_type: Type of agent that responded
            metadata: Additional metadata
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        # Store in vector memory
        self.vector_memory.add_conversation(
            conversation_id=session_id,
            user_message=user_message,
            agent_response=agent_response,
            agent_type=agent_type,
            metadata=metadata
        )

        # Update session info
        self.active_sessions[session_id]["message_count"] += 1
        self.active_sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()

    def get_context(
        self,
        session_id: str,
        max_messages: int = 5
    ) -> Dict[str, Any]:
        """Get conversation context for a session.

        Args:
            session_id: Session identifier
            max_messages: Maximum number of recent messages to include

        Returns:
            Context dictionary
        """
        if session_id not in self.active_sessions:
            return {}

        session_info = self.active_sessions[session_id]

        # Get recent conversation history
        history = self.vector_memory.get_conversation_history(
            conversation_id=session_id,
            limit=max_messages
        )

        return {
            "session_id": session_id,
            "brand_info": session_info["brand_info"],
            "conversation_history": history,
            "message_count": session_info["message_count"]
        }

    def search_relevant_content(
        self,
        session_id: str,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Search for relevant content from past conversations.

        Args:
            session_id: Session identifier
            query: Search query
            n_results: Number of results

        Returns:
            Relevant content items
        """
        return self.vector_memory.search_similar(
            query=query,
            n_results=n_results,
            filter_metadata={"conversation_id": session_id}
        )

    def end_session(self, session_id: str):
        """End a conversation session.

        Args:
            session_id: Session identifier
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a conversation session.

        Args:
            session_id: Session identifier

        Returns:
            Session summary
        """
        if session_id not in self.active_sessions:
            return {}

        session_info = self.active_sessions[session_id]
        history = self.vector_memory.get_conversation_history(
            conversation_id=session_id,
            limit=100
        )

        # Count agent usage
        agent_usage = {}
        for item in history:
            agent_type = item["metadata"].get("agent_type", "unknown")
            agent_usage[agent_type] = agent_usage.get(agent_type, 0) + 1

        return {
            "session_id": session_id,
            "created_at": session_info["created_at"],
            "last_activity": session_info["last_activity"],
            "total_messages": session_info["message_count"],
            "agent_usage": agent_usage,
            "brand_info": session_info["brand_info"]
        }
