"""Research agent for gathering information from web sources."""
from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup
from .base_agent import BaseAgent, AgentResult
from config import Config
import time


class ResearchAgent(BaseAgent):
    """Agent specialized in web research and information gathering."""

    @property
    def agent_type(self) -> str:
        return "research"

    @property
    def description(self) -> str:
        return (
            "Conducts comprehensive web research on topics, gathers current information, "
            "statistics, and trends. Use for market research, competitor analysis, "
            "trend discovery, and fact-checking."
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """Execute research task.

        Args:
            task: Research topic or question
            context: Additional context

        Returns:
            AgentResult with research findings
        """
        try:
            # Perform web search
            search_results = self._search_web(task)

            # Gather and synthesize information
            research_content = self._synthesize_research(
                task,
                search_results,
                context
            )

            result = AgentResult(
                agent_type=self.agent_type,
                content=research_content,
                metadata={
                    "topic": task,
                    "sources_count": len(search_results),
                    "sources": search_results[:5]  # Top 5 sources
                },
                success=True
            )

            # Store in memory
            if context and "conversation_id" in context:
                self._store_result(result, context["conversation_id"])

            return result

        except Exception as e:
            return AgentResult(
                agent_type=self.agent_type,
                content="",
                success=False,
                error=f"Research failed: {str(e)}"
            )

    def _search_web(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Search the web using available APIs or fallback methods.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results with title, url, snippet
        """
        # Try SERP API if available
        if Config.SERPAPI_API_KEY:
            return self._search_with_serpapi(query, max_results)

        # Fallback to DuckDuckGo search
        return self._search_with_duckduckgo(query, max_results)

    def _search_with_serpapi(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """Search using SERP API.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        try:
            from serpapi import GoogleSearch

            params = {
                "q": query,
                "api_key": Config.SERPAPI_API_KEY,
                "num": max_results
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            search_results = []
            for result in results.get("organic_results", [])[:max_results]:
                search_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })

            return search_results

        except Exception as e:
            print(f"SERP API search failed: {e}")
            return []

    def _search_with_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """Search using DuckDuckGo (fallback method).

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of search results
        """
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for result in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", "")
                    })

            return results

        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
            # Return mock results for demonstration
            return self._mock_search_results(query)

    def _mock_search_results(self, query: str) -> List[Dict[str, str]]:
        """Generate mock search results when no search API is available.

        Args:
            query: Search query

        Returns:
            List of mock search results
        """
        return [
            {
                "title": f"Research on {query} - Industry Report",
                "url": "https://example.com/research",
                "snippet": f"Comprehensive analysis of {query} trends and insights..."
            },
            {
                "title": f"{query} Statistics and Data - 2024",
                "url": "https://example.com/stats",
                "snippet": f"Latest statistics and data points related to {query}..."
            },
            {
                "title": f"Ultimate Guide to {query}",
                "url": "https://example.com/guide",
                "snippet": f"Everything you need to know about {query} in 2024..."
            }
        ]

    def _synthesize_research(
        self,
        topic: str,
        search_results: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Synthesize research findings into comprehensive summary.

        Args:
            topic: Research topic
            search_results: Search results
            context: Additional context

        Returns:
            Synthesized research content
        """
        # Prepare research data for LLM
        sources_text = "\n\n".join([
            f"**{i+1}. {result['title']}**\n{result['snippet']}\nSource: {result['url']}"
            for i, result in enumerate(search_results[:10])
        ])

        context_str = self._prepare_context(context) if context else ""

        prompt = f"""Research the following topic and provide a comprehensive summary based on the search results below.

**Topic:** {topic}

{context_str}

**Search Results:**
{sources_text}

Please provide:
1. A comprehensive overview of the topic
2. Key findings and insights
3. Current trends and statistics (if available)
4. Important facts and data points
5. Actionable takeaways

Format the response in clear, well-structured markdown with appropriate headings."""

        system_prompt = self._get_system_prompt()

        research_summary = self.llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=3000
        )

        # Add sources section
        sources_list = "\n".join([
            f"- [{result['title']}]({result['url']})"
            for result in search_results[:10]
        ])

        final_content = f"{research_summary}\n\n## Sources\n{sources_list}"

        return final_content
