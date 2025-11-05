"""Intelligent query routing to appropriate agents."""
from typing import List, Dict, Any, Optional
from utils.llm_client import LLMClient


class QueryRouter:
    """Routes user queries to appropriate agents based on intent."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize query router.

        Args:
            llm_client: LLM client for intent classification
        """
        self.llm_client = llm_client or LLMClient()

        # Define agent capabilities
        self.agent_capabilities = {
            "research": {
                "description": "Conducts web research, gathers information, statistics, and trends",
                "keywords": ["research", "find", "search", "data", "statistics", "trends", "information", "facts"],
                "examples": [
                    "Research the latest AI trends",
                    "Find statistics about content marketing",
                    "What are the current social media trends?"
                ]
            },
            "blog_writer": {
                "description": "Writes SEO-optimized blog posts and long-form articles",
                "keywords": ["blog", "article", "write", "post", "content", "seo", "guide", "tutorial"],
                "examples": [
                    "Write a blog post about digital marketing",
                    "Create an article on productivity tips",
                    "Write a comprehensive guide to SEO"
                ]
            },
            "reddit": {
                "description": "Creates Reddit posts and comments for community engagement",
                "keywords": ["reddit", "post", "discussion", "community", "social", "r/"],
                "examples": [
                    "Create a Reddit post about our new product",
                    "Write a discussion post for r/entrepreneur",
                    "Generate a Reddit comment"
                ]
            },
            "image": {
                "description": "Generates image prompts and creates visual content",
                "keywords": ["image", "visual", "graphic", "picture", "photo", "illustration", "banner", "header"],
                "examples": [
                    "Create an image for my blog header",
                    "Generate a social media graphic",
                    "Design a visual for my article"
                ]
            }
        }

    def route(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Route query to appropriate agent(s).

        Args:
            query: User query
            context: Additional context

        Returns:
            List of agent types that should handle this query
        """
        # First, try simple keyword matching
        keyword_matches = self._keyword_matching(query)

        # If clear match, return it
        if len(keyword_matches) == 1:
            return keyword_matches

        # Otherwise, use LLM for intelligent routing
        llm_routing = self._llm_routing(query, context)

        # Combine and deduplicate
        all_matches = list(set(keyword_matches + llm_routing))

        # If no matches, default to research + blog_writer
        if not all_matches:
            return ["research", "blog_writer"]

        return all_matches

    def _keyword_matching(self, query: str) -> List[str]:
        """Simple keyword-based routing.

        Args:
            query: User query

        Returns:
            List of matching agent types
        """
        query_lower = query.lower()
        matches = []

        for agent_type, info in self.agent_capabilities.items():
            keywords = info["keywords"]
            if any(keyword in query_lower for keyword in keywords):
                matches.append(agent_type)

        return matches

    def _llm_routing(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Use LLM for intelligent query routing.

        Args:
            query: User query
            context: Additional context

        Returns:
            List of agent types
        """
        # Prepare agent descriptions
        agent_descriptions = "\n".join([
            f"- **{agent}**: {info['description']}"
            for agent, info in self.agent_capabilities.items()
        ])

        context_str = ""
        if context:
            context_str = f"\nAdditional Context: {context}"

        prompt = f"""Analyze the following user query and determine which agent(s) should handle it.

**User Query:** {query}
{context_str}

**Available Agents:**
{agent_descriptions}

Instructions:
1. Identify the primary intent of the query
2. Determine which agent(s) are best suited to handle it
3. Multiple agents can be selected if the task requires it
4. For example, "Write a blog post about AI trends" might need both 'research' and 'blog_writer'

Output format: Return only the agent name(s), comma-separated. No explanation.
Valid agents: research, blog_writer, reddit, image

Examples:
Query: "Research AI trends and write a blog" -> research, blog_writer
Query: "Create a Reddit post about marketing" -> reddit
Query: "Generate a blog header image" -> image

Your response (agent names only):"""

        try:
            response = self.llm_client.generate(
                prompt=prompt,
                system_prompt="You are a query routing specialist. Output only agent names, comma-separated.",
                max_tokens=50
            )

            # Parse response
            agent_names = [name.strip().lower() for name in response.split(",")]

            # Validate agent names
            valid_agents = [
                name for name in agent_names
                if name in self.agent_capabilities
            ]

            return valid_agents if valid_agents else []

        except Exception as e:
            print(f"LLM routing failed: {e}")
            return []

    def suggest_workflow(self, query: str) -> Dict[str, Any]:
        """Suggest a workflow for complex queries.

        Args:
            query: User query

        Returns:
            Workflow suggestion with agent sequence and reasoning
        """
        agents = self.route(query)

        # Determine optimal sequence
        workflow = self._determine_sequence(agents, query)

        return {
            "agents": agents,
            "sequence": workflow["sequence"],
            "reasoning": workflow["reasoning"],
            "estimated_time": workflow["estimated_time"]
        }

    def _determine_sequence(self, agents: List[str], query: str) -> Dict[str, Any]:
        """Determine optimal agent execution sequence.

        Args:
            agents: List of agents
            query: User query

        Returns:
            Workflow information
        """
        # Define typical sequences
        if "research" in agents and "blog_writer" in agents:
            sequence = ["research", "blog_writer", "image"]
            reasoning = "First research the topic, then write the blog with findings, optionally add images"
            estimated_time = "3-5 minutes"

        elif "research" in agents and "reddit" in agents:
            sequence = ["research", "reddit"]
            reasoning = "Research the topic first, then create informed Reddit post"
            estimated_time = "2-3 minutes"

        elif "blog_writer" in agents and "image" in agents:
            sequence = ["blog_writer", "image"]
            reasoning = "Write the blog first, then generate relevant images"
            estimated_time = "2-4 minutes"

        elif len(agents) == 1:
            sequence = agents
            reasoning = f"Single agent task - {agents[0]}"
            estimated_time = "1-2 minutes"

        else:
            sequence = agents
            reasoning = "Execute agents in parallel or as specified"
            estimated_time = "2-4 minutes"

        return {
            "sequence": sequence,
            "reasoning": reasoning,
            "estimated_time": estimated_time
        }
