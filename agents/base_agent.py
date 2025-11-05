"""Base agent class for all ContentBlitz agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from utils.llm_client import LLMClient
from utils.vector_db import VectorMemory


@dataclass
class AgentResult:
    """Result from an agent execution."""

    agent_type: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_type": self.agent_type,
            "content": self.content,
            "metadata": self.metadata,
            "success": self.success,
            "error": self.error,
            "timestamp": self.timestamp
        }


class BaseAgent(ABC):
    """Base class for all content generation agents."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        memory: Optional[VectorMemory] = None,
        brand_voice: Optional[str] = None
    ):
        """Initialize base agent.

        Args:
            llm_client: LLM client for generation
            memory: Vector memory for context
            brand_voice: Brand voice guidelines
        """
        self.llm_client = llm_client or LLMClient()
        self.memory = memory
        self.brand_voice = brand_voice or "professional, informative, engaging"

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return the agent type identifier."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return the agent description for routing."""
        pass

    @abstractmethod
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """Execute the agent's task.

        Args:
            task: Task description
            context: Additional context (conversation history, brand info, etc.)

        Returns:
            AgentResult with generated content
        """
        pass

    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return f"""You are a {self.agent_type} agent in the ContentBlitz content marketing system.

Your role: {self.description}

Brand Voice Guidelines: {self.brand_voice}

Generate high-quality, on-brand content that meets the user's requirements."""

    def _prepare_context(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Prepare context string from context dictionary.

        Args:
            context: Context dictionary

        Returns:
            Formatted context string
        """
        if not context:
            return ""

        context_parts = []

        if "conversation_history" in context:
            context_parts.append("### Recent Conversation:")
            for msg in context["conversation_history"][-3:]:  # Last 3 messages
                # Handle both string messages and dict messages from memory
                if isinstance(msg, dict):
                    context_parts.append(msg.get("content", str(msg)))
                else:
                    context_parts.append(str(msg))

        if "target_audience" in context:
            context_parts.append(f"\n### Target Audience:\n{context['target_audience']}")

        if "keywords" in context:
            keywords = context['keywords']
            # Handle both list and string keywords
            if isinstance(keywords, list):
                keywords_str = ', '.join(str(k) for k in keywords)
            else:
                keywords_str = str(keywords)
            context_parts.append(f"\n### Target Keywords:\n{keywords_str}")

        if "tone" in context:
            context_parts.append(f"\n### Desired Tone:\n{context['tone']}")

        if "additional_info" in context:
            context_parts.append(f"\n### Additional Information:\n{context['additional_info']}")

        return "\n".join(context_parts)

    def _search_relevant_context(
        self,
        query: str,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Search for relevant context from memory.

        Args:
            query: Search query
            n_results: Number of results to retrieve

        Returns:
            List of relevant context items
        """
        if not self.memory:
            return []

        try:
            return self.memory.search_similar(query, n_results=n_results)
        except Exception as e:
            print(f"Error searching context: {e}")
            return []

    def _store_result(
        self,
        result: AgentResult,
        conversation_id: Optional[str] = None
    ):
        """Store result in memory for future reference.

        Args:
            result: Agent result to store
            conversation_id: Conversation identifier
        """
        if not self.memory:
            return

        try:
            content_id = f"{self.agent_type}_{result.timestamp}"
            self.memory.add_content(
                content_id=content_id,
                content=result.content,
                content_type=self.agent_type,
                metadata={
                    **result.metadata,
                    "conversation_id": conversation_id
                }
            )
        except Exception as e:
            print(f"Error storing result: {e}")
