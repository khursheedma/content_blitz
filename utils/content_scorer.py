"""Content performance scoring and quality assessment."""
from typing import Dict, Any, List, Optional
from .seo_analyzer import SEOAnalyzer
import re


class ContentPerformanceScorer:
    """Scores content quality and performance potential."""

    def __init__(self):
        """Initialize content scorer."""
        self.seo_analyzer = SEOAnalyzer()

    def score_content(
        self,
        content: str,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Score content performance potential.

        Args:
            content: Content to score
            content_type: Type of content (blog, reddit, etc.)
            metadata: Additional metadata

        Returns:
            Scoring results
        """
        if content_type in ["blog", "blog_writer", "article"]:
            return self._score_blog_content(content, metadata)
        elif content_type in ["reddit", "social"]:
            return self._score_social_content(content, metadata)
        elif content_type == "image":
            return self._score_image_content(content, metadata)
        else:
            return self._score_generic_content(content)

    def _score_blog_content(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Score blog post content.

        Args:
            content: Blog content
            metadata: Metadata

        Returns:
            Blog scoring results
        """
        scores = {
            "overall_score": 0,
            "category_scores": {},
            "strengths": [],
            "improvements": [],
            "details": {}
        }

        # SEO Score (30%)
        keywords = metadata.get("keywords", []) if metadata else []
        seo_analysis = self.seo_analyzer.analyze_content(content, keywords)

        seo_score = seo_analysis["score"]
        scores["category_scores"]["seo"] = seo_score

        if seo_score >= 70:
            scores["strengths"].append("Strong SEO optimization")
        else:
            scores["improvements"].append("SEO optimization needs improvement")

        # Readability Score (25%)
        readability = seo_analysis["readability"]
        flesch_score = readability.get("flesch_reading_ease", 0)

        readability_score = 0
        if 60 <= flesch_score <= 80:
            readability_score = 100
            scores["strengths"].append("Excellent readability")
        elif 50 <= flesch_score < 60:
            readability_score = 75
        elif 40 <= flesch_score < 50:
            readability_score = 50
            scores["improvements"].append("Simplify language for better readability")
        else:
            readability_score = 25
            scores["improvements"].append("Content is difficult to read")

        scores["category_scores"]["readability"] = readability_score

        # Structure Score (20%)
        structure_score = self._score_structure(content)
        scores["category_scores"]["structure"] = structure_score

        if structure_score >= 80:
            scores["strengths"].append("Well-structured content")
        else:
            scores["improvements"].append("Improve content structure")

        # Engagement Score (15%)
        engagement_score = self._score_engagement(content, "blog")
        scores["category_scores"]["engagement"] = engagement_score

        if engagement_score >= 75:
            scores["strengths"].append("High engagement potential")
        else:
            scores["improvements"].append("Add more engaging elements")

        # Length Score (10%)
        word_count = len(content.split())
        length_score = 0

        if 1000 <= word_count <= 2000:
            length_score = 100
            scores["strengths"].append(f"Optimal length ({word_count} words)")
        elif 500 <= word_count < 1000:
            length_score = 70
        elif word_count > 2000:
            length_score = 80
        else:
            length_score = 40
            scores["improvements"].append(f"Content too short ({word_count} words)")

        scores["category_scores"]["length"] = length_score

        # Calculate overall score
        scores["overall_score"] = (
            seo_score * 0.30 +
            readability_score * 0.25 +
            structure_score * 0.20 +
            engagement_score * 0.15 +
            length_score * 0.10
        )

        scores["details"] = {
            "word_count": word_count,
            "flesch_reading_ease": flesch_score,
            "seo_recommendations": seo_analysis["recommendations"]
        }

        return scores

    def _score_social_content(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Score social media content.

        Args:
            content: Social content
            metadata: Metadata

        Returns:
            Social scoring results
        """
        scores = {
            "overall_score": 0,
            "category_scores": {},
            "strengths": [],
            "improvements": [],
            "details": {}
        }

        # Engagement Score (40%)
        engagement_score = self._score_engagement(content, "social")
        scores["category_scores"]["engagement"] = engagement_score

        if engagement_score >= 80:
            scores["strengths"].append("High engagement potential")
        else:
            scores["improvements"].append("Make content more engaging")

        # Authenticity Score (30%)
        authenticity_score = self._score_authenticity(content)
        scores["category_scores"]["authenticity"] = authenticity_score

        if authenticity_score >= 75:
            scores["strengths"].append("Authentic, genuine tone")
        else:
            scores["improvements"].append("Make tone more authentic")

        # Formatting Score (20%)
        formatting_score = self._score_social_formatting(content)
        scores["category_scores"]["formatting"] = formatting_score

        if formatting_score >= 80:
            scores["strengths"].append("Well-formatted for social media")
        else:
            scores["improvements"].append("Improve formatting")

        # Length Score (10%)
        char_count = len(content)
        length_score = 0

        if 100 <= char_count <= 500:
            length_score = 100
            scores["strengths"].append("Optimal length for social")
        elif char_count > 1000:
            length_score = 50
            scores["improvements"].append("Consider shortening for social media")
        else:
            length_score = 70

        scores["category_scores"]["length"] = length_score

        # Calculate overall score
        scores["overall_score"] = (
            engagement_score * 0.40 +
            authenticity_score * 0.30 +
            formatting_score * 0.20 +
            length_score * 0.10
        )

        scores["details"] = {
            "character_count": char_count,
            "has_questions": "?" in content,
            "has_cta": any(cta in content.lower() for cta in ["what do you think", "share", "comment"])
        }

        return scores

    def _score_image_content(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Score image prompt quality.

        Args:
            content: Image prompt content
            metadata: Metadata

        Returns:
            Image scoring results
        """
        scores = {
            "overall_score": 75,  # Base score for image content
            "category_scores": {
                "specificity": 80,
                "clarity": 75,
                "technical": 70
            },
            "strengths": ["Image prompt generated"],
            "improvements": [],
            "details": {"prompt_length": len(content)}
        }

        return scores

    def _score_generic_content(self, content: str) -> Dict[str, Any]:
        """Score generic content.

        Args:
            content: Content to score

        Returns:
            Generic scoring results
        """
        word_count = len(content.split())

        return {
            "overall_score": 70,
            "category_scores": {
                "quality": 70
            },
            "strengths": ["Content generated successfully"],
            "improvements": [],
            "details": {"word_count": word_count}
        }

    def _score_structure(self, content: str) -> float:
        """Score content structure.

        Args:
            content: Content to analyze

        Returns:
            Structure score
        """
        score = 50  # Base score

        # Check for headings
        h1_count = len(re.findall(r'^#\s+', content, re.MULTILINE))
        h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        h3_count = len(re.findall(r'^###\s+', content, re.MULTILINE))

        if h1_count == 1:
            score += 15
        if h2_count >= 2:
            score += 15
        if h3_count >= 1:
            score += 10

        # Check for lists
        if re.search(r'^\s*[-*]\s+', content, re.MULTILINE):
            score += 10

        return min(100, score)

    def _score_engagement(self, content: str, content_type: str) -> float:
        """Score engagement potential.

        Args:
            content: Content to analyze
            content_type: Type of content

        Returns:
            Engagement score
        """
        score = 50  # Base score

        content_lower = content.lower()

        # Questions
        question_count = content.count("?")
        if question_count > 0:
            score += min(15, question_count * 5)

        # Call-to-action
        cta_phrases = ["what do you think", "share your", "let us know", "comment below", "tell us"]
        if any(phrase in content_lower for phrase in cta_phrases):
            score += 15

        # Personal pronouns (more engaging)
        personal_pronouns = ["you", "your", "we", "our"]
        pronoun_count = sum(content_lower.count(f" {p} ") for p in personal_pronouns)
        if pronoun_count >= 5:
            score += 10

        # Examples or stories
        example_indicators = ["example", "for instance", "imagine", "story", "case study"]
        if any(indicator in content_lower for indicator in example_indicators):
            score += 10

        return min(100, score)

    def _score_authenticity(self, content: str) -> float:
        """Score content authenticity.

        Args:
            content: Content to analyze

        Returns:
            Authenticity score
        """
        score = 60  # Base score

        content_lower = content.lower()

        # Personal indicators
        personal_indicators = ["i ", "my ", "we ", "our ", "experience"]
        if any(indicator in content_lower for indicator in personal_indicators):
            score += 15

        # Avoid corporate speak
        corporate_phrases = [
            "synergy", "leverage", "paradigm", "game-changer",
            "cutting-edge", "world-class", "best-in-class"
        ]
        corporate_count = sum(1 for phrase in corporate_phrases if phrase in content_lower)

        if corporate_count == 0:
            score += 15
        else:
            score -= corporate_count * 5

        # Natural language
        if "?" in content:
            score += 10

        return min(100, max(0, score))

    def _score_social_formatting(self, content: str) -> float:
        """Score social media formatting.

        Args:
            content: Content to analyze

        Returns:
            Formatting score
        """
        score = 60  # Base score

        # Check for short paragraphs (good for social)
        paragraphs = content.split("\n\n")
        avg_para_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0

        if avg_para_length <= 50:
            score += 20

        # Check for lists
        if re.search(r'^\s*[-*]\s+', content, re.MULTILINE):
            score += 10

        # Check for line breaks (mobile-friendly)
        if content.count("\n") >= 3:
            score += 10

        return min(100, score)
