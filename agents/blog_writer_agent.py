"""Blog writing agent with SEO optimization."""
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent, AgentResult
from utils.seo_analyzer import SEOAnalyzer


class BlogWriterAgent(BaseAgent):
    """Agent specialized in writing SEO-optimized blog posts."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seo_analyzer = SEOAnalyzer()

    @property
    def agent_type(self) -> str:
        return "blog_writer"

    @property
    def description(self) -> str:
        return (
            "Creates comprehensive, SEO-optimized blog posts and articles. "
            "Specializes in long-form content with proper structure, headings, "
            "keyword optimization, and engaging narrative. Use for blog posts, "
            "articles, guides, and educational content."
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """Execute blog writing task.

        Args:
            task: Blog topic or title
            context: Additional context (keywords, research, etc.)

        Returns:
            AgentResult with blog content
        """
        try:
            # Extract keywords from context
            keywords = context.get("keywords", []) if context else []

            # Get research context if available
            research_context = self._get_research_context(task)

            # Generate blog content
            blog_content = self._generate_blog(
                topic=task,
                keywords=keywords,
                research_context=research_context,
                context=context
            )

            # Perform SEO analysis
            seo_analysis = self.seo_analyzer.analyze_content(
                content=blog_content,
                target_keywords=keywords,
                title=task
            )

            # Optimize if needed
            if seo_analysis["score"] < 60:
                blog_content = self._optimize_content(
                    blog_content,
                    seo_analysis,
                    keywords
                )
                # Re-analyze
                seo_analysis = self.seo_analyzer.analyze_content(
                    content=blog_content,
                    target_keywords=keywords,
                    title=task
                )

            result = AgentResult(
                agent_type=self.agent_type,
                content=blog_content,
                metadata={
                    "topic": task,
                    "word_count": seo_analysis["word_count"],
                    "seo_score": seo_analysis["score"],
                    "keywords": keywords,
                    "readability": seo_analysis["readability"],
                    "recommendations": seo_analysis["recommendations"]
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
                error=f"Blog writing failed: {str(e)}"
            )

    def _get_research_context(self, topic: str) -> str:
        """Get relevant research context from memory.

        Args:
            topic: Blog topic

        Returns:
            Research context string
        """
        if not self.memory:
            return ""

        relevant_content = self._search_relevant_context(topic, n_results=2)

        if not relevant_content:
            return ""

        context_parts = ["### Relevant Research:"]
        for item in relevant_content:
            if item["metadata"].get("content_type") == "research":
                context_parts.append(f"\n{item['content'][:500]}...")

        return "\n".join(context_parts) if len(context_parts) > 1 else ""

    def _generate_blog(
        self,
        topic: str,
        keywords: List[str],
        research_context: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate blog content.

        Args:
            topic: Blog topic
            keywords: Target keywords
            research_context: Research findings
            context: Additional context

        Returns:
            Generated blog content
        """
        context_str = self._prepare_context(context) if context else ""

        keywords_str = ", ".join(keywords) if keywords else "relevant keywords"

        prompt = f"""Write a comprehensive, SEO-optimized blog post on the following topic:

**Topic:** {topic}

**Target Keywords:** {keywords_str}

{research_context}

{context_str}

Requirements:
1. Create an engaging, attention-grabbing title (use H1 heading)
2. Write a compelling introduction that hooks the reader
3. Structure content with clear H2 and H3 subheadings
4. Aim for 1000-1500 words for optimal SEO
5. Naturally incorporate target keywords (0.5-2% density)
6. Include actionable insights and practical tips
7. Write in an engaging, conversational style
8. Add a strong conclusion with call-to-action
9. Use bullet points and lists for better readability
10. Optimize for readability (Flesch Reading Ease score 60-80)

Brand Voice: {self.brand_voice}

Format the output in clean markdown with proper heading hierarchy."""

        system_prompt = self._get_system_prompt()

        blog_content = self.llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4000
        )

        return blog_content

    def _optimize_content(
        self,
        content: str,
        seo_analysis: Dict[str, Any],
        keywords: List[str]
    ) -> str:
        """Optimize content based on SEO analysis.

        Args:
            content: Original content
            seo_analysis: SEO analysis results
            keywords: Target keywords

        Returns:
            Optimized content
        """
        recommendations = seo_analysis["recommendations"]

        if not recommendations:
            return content

        optimization_prompt = f"""Optimize the following blog content based on these SEO recommendations:

**Recommendations:**
{chr(10).join(f'- {rec}' for rec in recommendations)}

**Target Keywords:** {', '.join(keywords)}

**Current SEO Score:** {seo_analysis['score']}/100

**Original Content:**
{content}

Please improve the content to address these recommendations while maintaining quality and readability. Keep the overall structure and key points, but enhance SEO elements."""

        system_prompt = "You are an SEO optimization specialist. Improve content while maintaining quality and brand voice."

        optimized_content = self.llm_client.generate(
            prompt=optimization_prompt,
            system_prompt=system_prompt,
            max_tokens=4000
        )

        return optimized_content

    def generate_with_outline(
        self,
        topic: str,
        outline: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Generate blog following a specific outline.

        Args:
            topic: Blog topic
            outline: List of section headings
            context: Additional context

        Returns:
            AgentResult with blog content
        """
        outline_str = "\n".join([f"{i+1}. {section}" for i, section in enumerate(outline)])

        context_with_outline = context or {}
        context_with_outline["additional_info"] = f"Follow this outline:\n{outline_str}"

        return self.execute(topic, context_with_outline)
