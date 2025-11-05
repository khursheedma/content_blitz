"""Unified LLM client supporting multiple providers."""
from typing import Optional, List, Dict, Any
from enum import Enum
import openai
from config import Config

# Optional imports for other providers
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class LLMProvider(Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"


class LLMClient:
    """Unified client for multiple LLM providers."""

    def __init__(
        self,
        provider: str = Config.DEFAULT_LLM_PROVIDER,
        model: Optional[str] = None,
        temperature: float = Config.TEMPERATURE
    ):
        """Initialize LLM client.

        Args:
            provider: LLM provider (anthropic, openai, google)
            model: Model name (provider-specific)
            temperature: Sampling temperature
        """
        self.provider = LLMProvider(provider)
        self.temperature = temperature

        # Set default model based on provider
        if model is None:
            model_defaults = {
                LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
                LLMProvider.OPENAI: "gpt-4-turbo-preview",
                LLMProvider.GOOGLE: "gemini-pro"
            }
            self.model = model_defaults[self.provider]
        else:
            self.model = model

        # Initialize client
        self._init_client()

    def _init_client(self):
        """Initialize the appropriate client based on provider."""
        if self.provider == LLMProvider.ANTHROPIC:
            if not ANTHROPIC_AVAILABLE:
                raise ValueError(
                    "Anthropic package not installed. "
                    "Install with: pip install anthropic"
                )
            if not Config.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

        elif self.provider == LLMProvider.OPENAI:
            if not Config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not configured")
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

        elif self.provider == LLMProvider.GOOGLE:
            if not GOOGLE_AVAILABLE:
                raise ValueError(
                    "Google Generative AI package not installed. "
                    "Install with: pip install google-generativeai"
                )
            if not Config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not configured")
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.client = genai.GenerativeModel(self.model)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        **kwargs
    ) -> str:
        """Generate text using the configured LLM.

        Args:
            prompt: User prompt
            system_prompt: System prompt (if supported)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text
        """
        try:
            if self.provider == LLMProvider.ANTHROPIC:
                return self._generate_anthropic(prompt, system_prompt, max_tokens, **kwargs)
            elif self.provider == LLMProvider.OPENAI:
                return self._generate_openai(prompt, system_prompt, max_tokens, **kwargs)
            elif self.provider == LLMProvider.GOOGLE:
                return self._generate_google(prompt, system_prompt, max_tokens, **kwargs)
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}")

    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using Anthropic Claude."""
        messages = [{"role": "user", "content": prompt}]

        params = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": self.temperature,
            "messages": messages
        }

        if system_prompt:
            params["system"] = system_prompt

        response = self.client.messages.create(**params)
        return response.content[0].text

    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using OpenAI GPT."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=self.temperature
        )

        return response.choices[0].message.content

    def _generate_google(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using Google Gemini."""
        # Combine system prompt with user prompt for Gemini
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        response = self.client.generate_content(
            full_prompt,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": max_tokens,
            }
        )

        return response.text

    async def generate_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        **kwargs
    ) -> str:
        """Async version of generate (for future implementation)."""
        # For now, just call sync version
        return self.generate(prompt, system_prompt, max_tokens, **kwargs)
