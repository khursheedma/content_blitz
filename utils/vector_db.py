"""Vector database for conversation memory and context."""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from datetime import datetime
import json
from config import Config


class VectorMemory:
    """ChromaDB-based vector memory for conversations and content."""

    def __init__(self, collection_name: str = "contentblitz_memory"):
        """Initialize vector memory.

        Args:
            collection_name: Name of the ChromaDB collection
        """
        self.client = chromadb.PersistentClient(
            path=Config.CHROMADB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_conversation(
        self,
        conversation_id: str,
        user_message: str,
        agent_response: str,
        agent_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store a conversation turn in memory.

        Args:
            conversation_id: Unique conversation identifier
            user_message: User's message
            agent_response: Agent's response
            agent_type: Type of agent that responded
            metadata: Additional metadata
        """
        doc_id = f"{conversation_id}_{datetime.utcnow().isoformat()}"

        combined_text = f"User: {user_message}\nAgent ({agent_type}): {agent_response}"

        meta = {
            "conversation_id": conversation_id,
            "agent_type": agent_type,
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message[:500],  # Truncate for metadata
        }

        if metadata:
            meta.update(metadata)

        self.collection.add(
            documents=[combined_text],
            ids=[doc_id],
            metadatas=[meta]
        )

    def add_content(
        self,
        content_id: str,
        content: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store generated content for future reference.

        Args:
            content_id: Unique content identifier
            content: The generated content
            content_type: Type of content (blog, reddit, image_prompt, etc.)
            metadata: Additional metadata
        """
        meta = {
            "content_type": content_type,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if metadata:
            meta.update(metadata)

        self.collection.add(
            documents=[content],
            ids=[content_id],
            metadatas=[meta]
        )

    def search_similar(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar content in memory.

        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Metadata filters (e.g., {"agent_type": "research"})

        Returns:
            List of similar items with metadata
        """
        where = filter_metadata if filter_metadata else None

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )

        items = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                items.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None
                })

        return items

    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve conversation history.

        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of messages to retrieve

        Returns:
            List of conversation turns
        """
        results = self.collection.get(
            where={"conversation_id": conversation_id},
            limit=limit
        )

        history = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                history.append({
                    "id": results["ids"][i],
                    "content": doc,
                    "metadata": results["metadatas"][i]
                })

        # Sort by timestamp
        history.sort(key=lambda x: x["metadata"].get("timestamp", ""))

        return history

    def clear_collection(self):
        """Clear all data from the collection."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
