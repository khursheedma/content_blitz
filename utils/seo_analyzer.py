"""SEO analysis and optimization utilities."""
from typing import Dict, List, Any, Optional
import re
from collections import Counter
import textstat
try:
    from rake_nltk import Rake
except ImportError:
    Rake = None


class SEOAnalyzer:
    """Analyze and score content for SEO optimization."""

    def __init__(self):
        """Initialize SEO analyzer."""
        self.rake = Rake() if Rake else None

    def analyze_content(
        self,
        content: str,
        target_keywords: Optional[List[str]] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive SEO analysis.

        Args:
            content: Content to analyze
            target_keywords: Keywords to optimize for
            title: Content title

        Returns:
            Dictionary with SEO metrics and recommendations
        """
        analysis = {
            "word_count": self._count_words(content),
            "readability": self._analyze_readability(content),
            "keywords": self._extract_keywords(content),
            "keyword_density": {},
            "heading_structure": self._analyze_headings(content),
            "recommendations": [],
            "score": 0.0
        }

        # Keyword analysis
        if target_keywords:
            analysis["keyword_density"] = self._calculate_keyword_density(
                content, target_keywords
            )
            analysis["keyword_in_title"] = self._check_keywords_in_title(
                title or "", target_keywords
            )

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)

        # Calculate overall SEO score
        analysis["score"] = self._calculate_seo_score(analysis)

        return analysis

    def _count_words(self, content: str) -> int:
        """Count words in content."""
        words = re.findall(r'\w+', content.lower())
        return len(words)

    def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability."""
        try:
            return {
                "flesch_reading_ease": round(textstat.flesch_reading_ease(content), 2),
                "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(content), 2),
                "automated_readability_index": round(textstat.automated_readability_index(content), 2),
            }
        except Exception as e:
            return {
                "flesch_reading_ease": 0,
                "flesch_kincaid_grade": 0,
                "automated_readability_index": 0,
                "error": str(e)
            }

    def _extract_keywords(self, content: str, top_n: int = 10) -> List[Dict[str, Any]]:
        """Extract keywords using RAKE algorithm."""
        if not self.rake:
            # Fallback: simple word frequency
            words = re.findall(r'\b[a-z]{4,}\b', content.lower())
            word_freq = Counter(words)
            return [
                {"keyword": word, "score": freq}
                for word, freq in word_freq.most_common(top_n)
            ]

        try:
            self.rake.extract_keywords_from_text(content)
            ranked_phrases = self.rake.get_ranked_phrases_with_scores()

            return [
                {"keyword": phrase, "score": round(score, 2)}
                for score, phrase in ranked_phrases[:top_n]
            ]
        except Exception:
            return []

    def _calculate_keyword_density(
        self,
        content: str,
        keywords: List[str]
    ) -> Dict[str, float]:
        """Calculate keyword density."""
        content_lower = content.lower()
        total_words = self._count_words(content)

        density = {}
        for keyword in keywords:
            count = content_lower.count(keyword.lower())
            density[keyword] = round((count / total_words) * 100, 2) if total_words > 0 else 0

        return density

    def _check_keywords_in_title(self, title: str, keywords: List[str]) -> Dict[str, bool]:
        """Check if keywords appear in title."""
        title_lower = title.lower()
        return {
            keyword: keyword.lower() in title_lower
            for keyword in keywords
        }

    def _analyze_headings(self, content: str) -> Dict[str, Any]:
        """Analyze heading structure (Markdown format)."""
        h1_count = len(re.findall(r'^#\s+.+$', content, re.MULTILINE))
        h2_count = len(re.findall(r'^##\s+.+$', content, re.MULTILINE))
        h3_count = len(re.findall(r'^###\s+.+$', content, re.MULTILINE))

        return {
            "h1_count": h1_count,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "total_headings": h1_count + h2_count + h3_count
        }

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate SEO recommendations based on analysis."""
        recommendations = []

        # Word count recommendations
        word_count = analysis["word_count"]
        if word_count < 300:
            recommendations.append("Content is too short. Aim for at least 300 words for better SEO.")
        elif word_count < 1000:
            recommendations.append("Consider expanding content to 1000+ words for better ranking potential.")

        # Readability recommendations
        readability = analysis["readability"]
        flesch_score = readability.get("flesch_reading_ease", 0)

        if flesch_score < 30:
            recommendations.append("Content is very difficult to read. Simplify language for better engagement.")
        elif flesch_score < 50:
            recommendations.append("Content is fairly difficult to read. Consider simplifying some sentences.")

        # Heading structure recommendations
        headings = analysis["heading_structure"]
        if headings["h1_count"] == 0:
            recommendations.append("Add an H1 heading for better content structure.")
        elif headings["h1_count"] > 1:
            recommendations.append("Use only one H1 heading. Use H2 and H3 for subheadings.")

        if headings["h2_count"] == 0 and word_count > 500:
            recommendations.append("Add H2 subheadings to improve content structure and readability.")

        # Keyword recommendations
        if "keyword_density" in analysis:
            for keyword, density in analysis["keyword_density"].items():
                if density < 0.5:
                    recommendations.append(f"Keyword '{keyword}' appears too infrequently. Target 0.5-2.5% density.")
                elif density > 3:
                    recommendations.append(f"Keyword '{keyword}' may be over-optimized. Reduce usage to avoid keyword stuffing.")

        return recommendations

    def _calculate_seo_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall SEO score (0-100)."""
        score = 0.0

        # Word count (20 points)
        word_count = analysis["word_count"]
        if word_count >= 1500:
            score += 20
        elif word_count >= 1000:
            score += 15
        elif word_count >= 500:
            score += 10
        elif word_count >= 300:
            score += 5

        # Readability (20 points)
        flesch_score = analysis["readability"].get("flesch_reading_ease", 0)
        if 60 <= flesch_score <= 80:
            score += 20
        elif 50 <= flesch_score < 60 or 80 < flesch_score <= 90:
            score += 15
        elif flesch_score >= 40:
            score += 10

        # Heading structure (15 points)
        headings = analysis["heading_structure"]
        if headings["h1_count"] == 1:
            score += 5
        if headings["h2_count"] >= 2:
            score += 5
        if headings["total_headings"] >= 3:
            score += 5

        # Keyword optimization (25 points)
        if "keyword_density" in analysis:
            optimal_keywords = sum(
                1 for density in analysis["keyword_density"].values()
                if 0.5 <= density <= 2.5
            )
            total_keywords = len(analysis["keyword_density"])
            if total_keywords > 0:
                score += (optimal_keywords / total_keywords) * 25

        # Keywords in title (20 points)
        if "keyword_in_title" in analysis:
            keywords_in_title = sum(analysis["keyword_in_title"].values())
            total_keywords = len(analysis["keyword_in_title"])
            if total_keywords > 0:
                score += (keywords_in_title / total_keywords) * 20

        return round(score, 2)

    def suggest_improvements(
        self,
        content: str,
        target_keywords: Optional[List[str]] = None
    ) -> str:
        """Generate improvement suggestions as formatted text.

        Args:
            content: Content to analyze
            target_keywords: Target keywords

        Returns:
            Formatted improvement suggestions
        """
        analysis = self.analyze_content(content, target_keywords)

        output = [
            "### SEO Analysis Report",
            f"**Overall Score:** {analysis['score']}/100",
            "",
            f"**Word Count:** {analysis['word_count']}",
            f"**Readability Score:** {analysis['readability']['flesch_reading_ease']} (Flesch Reading Ease)",
            "",
            "### Recommendations:",
        ]

        for i, rec in enumerate(analysis["recommendations"], 1):
            output.append(f"{i}. {rec}")

        if not analysis["recommendations"]:
            output.append("Great job! No major improvements needed.")

        return "\n".join(output)
