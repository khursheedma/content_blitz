"""Brand voice management and consistency."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json


@dataclass
class BrandProfile:
    """Brand profile configuration."""

    brand_name: str
    voice_attributes: List[str]  # e.g., ["professional", "friendly", "authoritative"]
    target_audience: str
    industry: str
    tone_guidelines: str
    keywords: List[str] = None
    writing_style: str = "clear and concise"
    avoid_words: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrandProfile":
        """Create from dictionary."""
        return cls(**data)


class BrandVoiceManager:
    """Manages brand voice consistency across content."""

    def __init__(self):
        """Initialize brand voice manager."""
        self.profiles: Dict[str, BrandProfile] = {}
        self.active_profile: Optional[BrandProfile] = None

    def create_profile(
        self,
        brand_name: str,
        voice_attributes: List[str],
        target_audience: str,
        industry: str,
        tone_guidelines: str,
        **kwargs
    ) -> BrandProfile:
        """Create a new brand profile.

        Args:
            brand_name: Brand name
            voice_attributes: List of voice attributes
            target_audience: Target audience description
            industry: Industry/vertical
            tone_guidelines: Detailed tone guidelines
            **kwargs: Additional profile attributes

        Returns:
            Created brand profile
        """
        profile = BrandProfile(
            brand_name=brand_name,
            voice_attributes=voice_attributes,
            target_audience=target_audience,
            industry=industry,
            tone_guidelines=tone_guidelines,
            **kwargs
        )

        self.profiles[brand_name] = profile

        # Set as active if it's the first profile
        if not self.active_profile:
            self.active_profile = profile

        return profile

    def set_active_profile(self, brand_name: str):
        """Set the active brand profile.

        Args:
            brand_name: Brand name
        """
        if brand_name not in self.profiles:
            raise ValueError(f"Brand profile '{brand_name}' not found")

        self.active_profile = self.profiles[brand_name]

    def get_voice_guidelines(self, profile_name: Optional[str] = None) -> str:
        """Get voice guidelines as formatted string.

        Args:
            profile_name: Specific profile name, or use active profile

        Returns:
            Formatted voice guidelines
        """
        profile = self.profiles.get(profile_name) if profile_name else self.active_profile

        if not profile:
            return "Professional, informative, and engaging"

        guidelines = f"""Brand: {profile.brand_name}

Voice Attributes: {', '.join(profile.voice_attributes)}

Target Audience: {profile.target_audience}

Industry: {profile.industry}

Tone Guidelines:
{profile.tone_guidelines}

Writing Style: {profile.writing_style}"""

        if profile.keywords:
            guidelines += f"\n\nKey Topics/Keywords: {', '.join(profile.keywords)}"

        if profile.avoid_words:
            guidelines += f"\n\nWords to Avoid: {', '.join(profile.avoid_words)}"

        return guidelines

    def get_context_for_agent(self, profile_name: Optional[str] = None) -> Dict[str, Any]:
        """Get brand context for agent execution.

        Args:
            profile_name: Specific profile name, or use active profile

        Returns:
            Brand context dictionary
        """
        profile = self.profiles.get(profile_name) if profile_name else self.active_profile

        if not profile:
            return {}

        return {
            "brand_name": profile.brand_name,
            "brand_voice": self.get_voice_guidelines(profile_name),
            "target_audience": profile.target_audience,
            "keywords": profile.keywords or [],
            "tone": ", ".join(profile.voice_attributes)
        }

    def analyze_content_consistency(
        self,
        content: str,
        profile_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze how well content matches brand voice.

        Args:
            content: Content to analyze
            profile_name: Specific profile name, or use active profile

        Returns:
            Analysis results
        """
        profile = self.profiles.get(profile_name) if profile_name else self.active_profile

        if not profile:
            return {"score": 0, "feedback": "No brand profile configured"}

        score = 50  # Base score
        feedback = []

        content_lower = content.lower()

        # Check for keywords
        if profile.keywords:
            keyword_count = sum(1 for kw in profile.keywords if kw.lower() in content_lower)
            keyword_percentage = (keyword_count / len(profile.keywords)) * 100

            if keyword_percentage > 50:
                score += 20
                feedback.append(f"✓ Good keyword usage ({keyword_percentage:.0f}% of target keywords present)")
            else:
                feedback.append(f"⚠ Consider adding more brand keywords ({keyword_percentage:.0f}% present)")

        # Check for avoid words
        if profile.avoid_words:
            avoid_found = [word for word in profile.avoid_words if word.lower() in content_lower]

            if avoid_found:
                score -= 10
                feedback.append(f"⚠ Contains words to avoid: {', '.join(avoid_found)}")
            else:
                score += 15
                feedback.append("✓ No flagged words present")

        # Basic length check
        word_count = len(content.split())
        if word_count >= 300:
            score += 15
            feedback.append(f"✓ Good content length ({word_count} words)")
        else:
            feedback.append(f"⚠ Content might be too short ({word_count} words)")

        return {
            "score": min(100, max(0, score)),
            "feedback": feedback,
            "profile_used": profile.brand_name
        }

    def save_profile(self, profile_name: str, file_path: str):
        """Save brand profile to JSON file.

        Args:
            profile_name: Profile name
            file_path: Path to save file
        """
        if profile_name not in self.profiles:
            raise ValueError(f"Profile '{profile_name}' not found")

        profile = self.profiles[profile_name]

        with open(file_path, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)

    def load_profile(self, file_path: str) -> BrandProfile:
        """Load brand profile from JSON file.

        Args:
            file_path: Path to profile file

        Returns:
            Loaded brand profile
        """
        with open(file_path, 'r') as f:
            data = json.load(f)

        profile = BrandProfile.from_dict(data)
        self.profiles[profile.brand_name] = profile

        return profile
