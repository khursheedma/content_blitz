"""Image generation agent for visual content creation."""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent, AgentResult
from config import Config
from PIL import Image, ImageDraw, ImageFont
import io
import base64


class ImageAgent(BaseAgent):
    """Agent specialized in generating and describing images for content."""

    @property
    def agent_type(self) -> str:
        return "image"

    @property
    def description(self) -> str:
        return (
            "Creates image prompts and generates visuals for blog posts, social media, "
            "and marketing content. Can generate AI art prompts optimized for various "
            "image generation models, and create placeholder graphics. "
            "Use for blog headers, social media graphics, and visual content."
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResult:
        """Execute image generation task.

        Args:
            task: Image description or theme
            context: Additional context (style, dimensions, purpose, etc.)

        Returns:
            AgentResult with image prompt and/or generated image
        """
        try:
            # Determine if we should generate an actual image or just a prompt
            generate_image = context.get("generate_image", False) if context else False

            # Generate optimized image prompt
            image_prompt = self._generate_image_prompt(task, context)

            metadata = {
                "task": task,
                "image_prompt": image_prompt
            }

            content = f"## Image Prompt\n\n{image_prompt}\n\n"

            # Generate placeholder or actual image if requested
            if generate_image:
                if Config.STABILITY_API_KEY:
                    # Use Stability AI for actual generation
                    image_result = self._generate_with_stability(image_prompt)
                    metadata["image_generated"] = True
                    metadata["image_data"] = image_result
                    content += "✓ Image generated successfully with Stability AI.\n"
                else:
                    # Generate placeholder
                    placeholder = self._generate_placeholder(task, context)
                    metadata["placeholder_generated"] = True
                    metadata["image_data"] = placeholder
                    content += "✓ Placeholder image generated (configure STABILITY_API_KEY for AI generation).\n"

            content += "\n### Usage Guidelines\n"
            content += self._generate_usage_guidelines(task, context)

            result = AgentResult(
                agent_type=self.agent_type,
                content=content,
                metadata=metadata,
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
                error=f"Image generation failed: {str(e)}"
            )

    def _generate_image_prompt(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate optimized image prompt for AI image generation.

        Args:
            task: Image description
            context: Additional context

        Returns:
            Optimized image prompt
        """
        style = context.get("style", "professional, modern") if context else "professional, modern"
        purpose = context.get("purpose", "blog header") if context else "blog header"
        context_str = self._prepare_context(context) if context else ""

        prompt = f"""Create a detailed, optimized image generation prompt for the following:

**Subject:** {task}

**Purpose:** {purpose}

**Style:** {style}

{context_str}

Generate a comprehensive prompt that includes:
1. Main subject and composition
2. Style and artistic direction
3. Color palette and mood
4. Lighting and atmosphere
5. Technical details (quality, resolution descriptors)
6. Specific elements to include/exclude

Format as a single, detailed prompt suitable for Midjourney, DALL-E, or Stable Diffusion.
Include quality modifiers like: high quality, detailed, professional, 4k, sharp focus, etc."""

        system_prompt = """You are an expert at creating prompts for AI image generation.
Create detailed, specific prompts that will produce high-quality, relevant images."""

        image_prompt = self.llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=500
        )

        return image_prompt.strip()

    def _generate_with_stability(self, prompt: str) -> str:
        """Generate image using Stability AI.

        Args:
            prompt: Image prompt

        Returns:
            Base64 encoded image data
        """
        try:
            import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
            from stability_sdk import client

            stability_api = client.StabilityInference(
                key=Config.STABILITY_API_KEY,
                verbose=True,
            )

            answers = stability_api.generate(
                prompt=prompt,
                width=1024,
                height=1024,
            )

            for resp in answers:
                for artifact in resp.artifacts:
                    if artifact.type == generation.ARTIFACT_IMAGE:
                        img_data = artifact.binary
                        return base64.b64encode(img_data).decode('utf-8')

            return ""

        except Exception as e:
            print(f"Stability AI generation failed: {e}")
            return ""

    def _generate_placeholder(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a simple placeholder image.

        Args:
            task: Image description
            context: Additional context

        Returns:
            Base64 encoded placeholder image
        """
        # Get dimensions from context or use defaults
        width = context.get("width", 1200) if context else 1200
        height = context.get("height", 630) if context else 630

        # Create simple gradient placeholder
        img = Image.new('RGB', (width, height), color=(100, 150, 200))
        draw = ImageDraw.Draw(img)

        # Add text
        text = task[:50] if len(task) > 50 else task

        # Draw text in center (simplified - doesn't handle complex text wrapping)
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        position = ((width - text_width) // 2, (height - text_height) // 2)
        draw.text(position, text, fill=(255, 255, 255))

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return img_data

    def _generate_usage_guidelines(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate usage guidelines for the image.

        Args:
            task: Image description
            context: Additional context

        Returns:
            Usage guidelines text
        """
        purpose = context.get("purpose", "blog header") if context else "blog header"

        guidelines = f"""
**Recommended Platforms:**
- Blog posts and articles
- Social media (Facebook, LinkedIn, Twitter)
- Email newsletters
- Marketing materials

**Best Practices:**
- Ensure image aligns with brand guidelines
- Add alt text for accessibility: "{task}"
- Optimize file size for web (compress if needed)
- Use appropriate dimensions for platform ({purpose})
- Consider mobile viewing experience

**SEO Tips:**
- Use descriptive file names (e.g., {task.lower().replace(' ', '-')[:30]}.jpg)
- Include relevant keywords in alt text
- Compress images to improve page load speed
"""
        return guidelines

    def suggest_alt_text(self, image_description: str) -> str:
        """Generate SEO-optimized alt text for an image.

        Args:
            image_description: Description of the image

        Returns:
            SEO-optimized alt text
        """
        prompt = f"""Generate concise, SEO-optimized alt text for an image with this description:

{image_description}

Requirements:
- Keep it under 125 characters
- Be descriptive and specific
- Include relevant keywords naturally
- Focus on what's important for accessibility
- Avoid "image of" or "picture of" prefixes

Output only the alt text, nothing else."""

        alt_text = self.llm_client.generate(
            prompt=prompt,
            system_prompt="You are an accessibility and SEO expert.",
            max_tokens=100
        )

        return alt_text.strip().strip('"')
