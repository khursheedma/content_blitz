"""Main orchestrator coordinating all agents."""
from typing import Dict, Any, Optional, List
from agents import (
    ResearchAgent,
    BlogWriterAgent,
    RedditAgent,
    ImageAgent,
    AgentResult
)
from .query_router import QueryRouter
from .brand_voice import BrandVoiceManager, BrandProfile
from .memory import ConversationMemory
from utils.llm_client import LLMClient
from utils.vector_db import VectorMemory
import time


class ContentOrchestrator:
    """Orchestrates multiple agents to handle complex content generation tasks."""

    def __init__(
        self,
        llm_provider: str = "openai",
        model: Optional[str] = None
    ):
        """Initialize content orchestrator.

        Args:
            llm_provider: LLM provider to use (default: openai)
            model: Specific model name
        """
        # Initialize core components
        self.llm_client = LLMClient(provider=llm_provider, model=model)
        self.vector_memory = VectorMemory()
        self.brand_manager = BrandVoiceManager()
        self.memory = ConversationMemory()
        self.router = QueryRouter(self.llm_client)

        # Initialize agents
        self.agents = {
            "research": ResearchAgent(
                llm_client=self.llm_client,
                memory=self.vector_memory
            ),
            "blog_writer": BlogWriterAgent(
                llm_client=self.llm_client,
                memory=self.vector_memory
            ),
            "reddit": RedditAgent(
                llm_client=self.llm_client,
                memory=self.vector_memory
            ),
            "image": ImageAgent(
                llm_client=self.llm_client,
                memory=self.vector_memory
            )
        }

        self.current_session: Optional[str] = None

    def start_session(self, brand_profile: Optional[BrandProfile] = None) -> str:
        """Start a new content generation session.

        Args:
            brand_profile: Brand profile for this session

        Returns:
            Session ID
        """
        brand_info = brand_profile.to_dict() if brand_profile else {}
        session_id = self.memory.create_session(brand_info)
        self.current_session = session_id

        # Update brand voice in agents if profile provided
        if brand_profile:
            brand_voice = self.brand_manager.get_voice_guidelines()
            for agent in self.agents.values():
                agent.brand_voice = brand_voice

        return session_id

    def process_request(
        self,
        request: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a content generation request.

        Args:
            request: User request
            session_id: Session ID (uses current session if not provided)
            context: Additional context

        Returns:
            Dictionary with results from all agents
        """
        # Use current session if not specified
        if not session_id:
            session_id = self.current_session

        if not session_id:
            session_id = self.start_session()

        # Get conversation context
        conversation_context = self.memory.get_context(session_id)

        # Merge with provided context
        full_context = {**conversation_context, **(context or {})}
        full_context["conversation_id"] = session_id

        # Route query to appropriate agents
        agent_types = self.router.route(request, full_context)

        print(f"🎯 Routing to agents: {', '.join(agent_types)}")

        # Execute agents
        results = {}
        for agent_type in agent_types:
            if agent_type in self.agents:
                print(f"🤖 Executing {agent_type} agent...")

                agent = self.agents[agent_type]
                result = agent.execute(request, full_context)

                results[agent_type] = result

                # Store in memory
                if result.success:
                    self.memory.add_message(
                        session_id=session_id,
                        user_message=request,
                        agent_response=result.content,
                        agent_type=agent_type,
                        metadata=result.metadata
                    )

        return {
            "session_id": session_id,
            "request": request,
            "agents_used": agent_types,
            "results": results,
            "timestamp": time.time()
        }

    def execute_workflow(
        self,
        workflow: List[str],
        initial_request: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, AgentResult]:
        """Execute a specific workflow of agents in sequence.

        Args:
            workflow: List of agent types in execution order
            initial_request: Initial user request
            session_id: Session ID
            context: Additional context

        Returns:
            Dictionary of agent results
        """
        if not session_id:
            session_id = self.current_session or self.start_session()

        results = {}
        accumulated_context = context or {}
        accumulated_context["conversation_id"] = session_id

        for agent_type in workflow:
            if agent_type not in self.agents:
                print(f"⚠️  Agent '{agent_type}' not found, skipping...")
                continue

            print(f"🤖 Executing {agent_type} agent in workflow...")

            agent = self.agents[agent_type]

            # Use previous results as context for next agent
            if results:
                accumulated_context["previous_results"] = {
                    k: v.content for k, v in results.items()
                }

            result = agent.execute(initial_request, accumulated_context)
            results[agent_type] = result

            # Store in memory
            if result.success:
                self.memory.add_message(
                    session_id=session_id,
                    user_message=initial_request,
                    agent_response=result.content,
                    agent_type=agent_type,
                    metadata=result.metadata
                )

        return results

    def generate_content_package(
        self,
        topic: str,
        formats: List[str],
        session_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a complete content package with multiple formats.

        Args:
            topic: Content topic
            formats: List of formats (blog, reddit, image, etc.)
            session_id: Session ID
            **kwargs: Additional parameters

        Returns:
            Complete content package
        """
        if not session_id:
            session_id = self.start_session()

        # Step 1: Research (if needed)
        research_result = None
        if kwargs.get("include_research", True):
            print("🔍 Conducting research...")
            research_result = self.agents["research"].execute(
                topic,
                {"conversation_id": session_id}
            )

        # Prepare context with research findings
        context = {"conversation_id": session_id}
        if research_result and research_result.success:
            context["research"] = research_result.content
            context["additional_info"] = f"Use these research findings:\n\n{research_result.content[:1000]}"

        # Add any additional context
        context.update(kwargs)

        # Step 2: Generate requested formats
        package = {
            "topic": topic,
            "research": research_result,
            "content": {}
        }

        format_agent_mapping = {
            "blog": "blog_writer",
            "article": "blog_writer",
            "reddit": "reddit",
            "social": "reddit",
            "image": "image",
            "visual": "image"
        }

        for format_type in formats:
            agent_type = format_agent_mapping.get(format_type.lower())

            if agent_type and agent_type in self.agents:
                print(f"📝 Generating {format_type} content...")

                result = self.agents[agent_type].execute(topic, context)
                package["content"][format_type] = result

        return package

    def get_session_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of a session.

        Args:
            session_id: Session ID (uses current if not provided)

        Returns:
            Session summary
        """
        sid = session_id or self.current_session

        if not sid:
            return {}

        return self.memory.get_session_summary(sid)

    def set_brand_profile(self, profile: BrandProfile):
        """Set the active brand profile for the orchestrator.

        Args:
            profile: Brand profile
        """
        self.brand_manager.profiles[profile.brand_name] = profile
        self.brand_manager.set_active_profile(profile.brand_name)

        # Update agents
        brand_voice = self.brand_manager.get_voice_guidelines()
        for agent in self.agents.values():
            agent.brand_voice = brand_voice
