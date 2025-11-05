"""Reddit post generation agent."""
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent, AgentResult


class RedditAgent(BaseAgent):
    """Agent specialized in creating Reddit posts and comments."""

    @property
    def agent_type(self) -> str:
        return "reddit"

    @property
    def description(self) -> str:
        return (
            "Creates engaging Reddit posts, comments, and discussions. "
            "Understands Reddit culture, formatting, and best practices. "
            "Can generate posts for different subreddits with appropriate tone. "
            "Use for social engagement, community building, and discussions."
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """Execute Reddit post generation task.

        Args:
            task: Post topic or prompt
            context: Additional context (subreddit, post type, etc.)

        Returns:
            AgentResult with Reddit post
        """
        try:
            # Determine post type and subreddit from context
            post_type = context.get("post_type", "discussion") if context else "discussion"
            subreddit = context.get("subreddit", "general") if context else "general"

            # Generate Reddit post
            reddit_content = self._generate_reddit_post(
                topic=task,
                post_type=post_type,
                subreddit=subreddit,
                context=context
            )

            # Analyze engagement potential
            engagement_score = self._analyze_engagement_potential(reddit_content)

            result = AgentResult(
                agent_type=self.agent_type,
                content=reddit_content,
                metadata={
                    "topic": task,
                    "post_type": post_type,
                    "subreddit": subreddit,
                    "engagement_score": engagement_score,
                    "character_count": len(reddit_content)
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
                error=f"Reddit post generation failed: {str(e)}"
            )

    def _generate_reddit_post(
        self,
        topic: str,
        post_type: str,
        subreddit: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate Reddit post content.

        Args:
            topic: Post topic
            post_type: Type of post (discussion, question, story, advice, etc.)
            subreddit: Target subreddit
            context: Additional context

        Returns:
            Generated Reddit post
        """
        context_str = self._prepare_context(context) if context else ""

        # Get subreddit-specific guidelines
        subreddit_guidelines = self._get_subreddit_guidelines(subreddit)

        prompt = f"""Create an engaging Reddit post for r/{subreddit}.

**Topic:** {topic}

**Post Type:** {post_type}

**Subreddit Guidelines:**
{subreddit_guidelines}

{context_str}

Requirements:
1. Write an attention-grabbing title (keep it under 300 characters)
2. Create engaging post content that follows Reddit's informal, conversational tone
3. Use proper Reddit formatting (markdown, bullet points, line breaks)
4. Be authentic and avoid corporate/salesy language
5. Encourage discussion and engagement
6. Add relevant questions to prompt comments
7. Use appropriate emojis sparingly (only if fitting for the subreddit)
8. Keep paragraphs short for mobile readability

Reddit Formatting Tips:
- Use **bold** for emphasis
- Use bullet points with * or -
- Add line breaks between paragraphs
- Quote with > if needed

Brand Voice (adapt for Reddit): {self.brand_voice}

Output format:
**Title:** [Your catchy title here]

**Post Content:**
[Your post content here]"""

        system_prompt = """You are a Reddit content specialist who understands Reddit culture, tone, and engagement patterns.
Create authentic, engaging posts that resonate with Reddit communities while avoiding corporate speak."""

        reddit_post = self.llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000
        )

        return reddit_post

    def _get_subreddit_guidelines(self, subreddit: str) -> str:
        """Get guidelines for specific subreddit.

        Args:
            subreddit: Subreddit name

        Returns:
            Guidelines string
        """
        # Common guidelines for popular subreddits
        guidelines = {
            "entrepreneur": "Focus on business insights, startup experiences, and practical advice. Be genuine and share real experiences.",
            "marketing": "Share data-driven insights, case studies, and actionable strategies. Avoid blatant self-promotion.",
            "content_marketing": "Discuss strategy, best practices, and content creation tips. Share examples and results.",
            "smallbusiness": "Provide practical advice for small business owners. Be supportive and helpful.",
            "socialmedia": "Discuss social media trends, strategies, and platform updates. Share insights and tips.",
            "seo": "Share technical insights, algorithm updates, and optimization strategies. Back claims with data.",
            "general": "Be engaging, authentic, and conversational. Follow general Reddit etiquette."
        }

        return guidelines.get(
            subreddit.lower(),
            "Be authentic, engaging, and follow general Reddit community guidelines. Add value to the discussion."
        )

    def _analyze_engagement_potential(self, content: str) -> float:
        """Analyze potential engagement score for Reddit post.

        Args:
            content: Post content

        Returns:
            Engagement score (0-100)
        """
        score = 50.0  # Base score

        # Check for question marks (encourages discussion)
        if "?" in content:
            score += 15

        # Check for personal experience indicators
        personal_indicators = ["I", "my", "we", "our", "experience", "learned"]
        if any(indicator in content.lower() for indicator in personal_indicators):
            score += 10

        # Check for call-to-action
        cta_indicators = ["what do you think", "thoughts?", "opinions?", "share your", "anyone else"]
        if any(cta in content.lower() for cta in cta_indicators):
            score += 15

        # Check length (not too short, not too long)
        word_count = len(content.split())
        if 100 <= word_count <= 500:
            score += 10
        elif word_count > 1000:
            score -= 10

        return min(100, max(0, score))

    def generate_comment(
        self,
        parent_post: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Generate a Reddit comment in response to a post.

        Args:
            parent_post: The post to comment on
            context: Additional context

        Returns:
            AgentResult with comment content
        """
        prompt = f"""Create a thoughtful Reddit comment in response to this post:

{parent_post}

Requirements:
1. Add value to the discussion
2. Be conversational and authentic
3. Keep it concise (3-5 paragraphs max)
4. Use proper Reddit formatting
5. Avoid being preachy or salesy

Output the comment directly (no "Comment:" prefix needed)."""

        system_prompt = "You are a helpful Reddit community member providing thoughtful, valuable comments."

        comment = self.llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1000
        )

        return AgentResult(
            agent_type=f"{self.agent_type}_comment",
            content=comment,
            metadata={"parent_post_preview": parent_post[:100]},
            success=True
        )
