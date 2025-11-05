"""Example usage of ContentBlitz programmatically."""

from core.orchestrator import ContentOrchestrator
from core.brand_voice import BrandProfile


def example_simple_generation():
    """Example: Simple content generation."""
    print("=" * 60)
    print("Example 1: Simple Content Generation")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = ContentOrchestrator()

    # Start session
    session_id = orchestrator.start_session()
    print(f"✓ Session started: {session_id}\n")

    # Generate content
    print("Generating blog post about AI trends...")
    result = orchestrator.process_request(
        request="Write a short blog post about AI trends in 2024",
        context={
            "keywords": ["AI", "artificial intelligence", "trends", "2024"]
        }
    )

    # Display results
    print(f"\n✓ Generated content using agents: {', '.join(result['agents_used'])}\n")

    for agent_type, agent_result in result["results"].items():
        if agent_result.success:
            print(f"\n--- {agent_type.upper()} RESULT ---")
            print(agent_result.content[:500] + "...\n")
            print(f"Metadata: {agent_result.metadata}\n")
        else:
            print(f"❌ {agent_type} failed: {agent_result.error}")


def example_with_brand_voice():
    """Example: Content generation with brand voice."""
    print("\n" + "=" * 60)
    print("Example 2: Content Generation with Brand Voice")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = ContentOrchestrator()

    # Create brand profile
    brand = BrandProfile(
        brand_name="TechStartup Inc",
        voice_attributes=["innovative", "technical", "friendly"],
        target_audience="developers and tech enthusiasts",
        industry="technology",
        tone_guidelines="Be technical but accessible. Use examples and analogies. Keep it conversational."
    )

    print(f"✓ Created brand profile: {brand.brand_name}")

    # Set brand profile
    orchestrator.set_brand_profile(brand)

    # Start session
    session_id = orchestrator.start_session(brand)
    print(f"✓ Session started with brand profile\n")

    # Generate content
    print("Generating Reddit post with brand voice...")
    result = orchestrator.process_request(
        request="Create a Reddit post about our new API for r/programming",
        context={
            "post_type": "announcement",
            "subreddit": "programming"
        }
    )

    # Display results
    for agent_type, agent_result in result["results"].items():
        if agent_result.success:
            print(f"\n--- {agent_type.upper()} RESULT ---")
            print(agent_result.content[:400] + "...\n")


def example_content_package():
    """Example: Complete content package generation."""
    print("\n" + "=" * 60)
    print("Example 3: Complete Content Package")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = ContentOrchestrator()

    # Generate content package
    print("Generating content package about machine learning...")

    package = orchestrator.generate_content_package(
        topic="Machine Learning for Beginners",
        formats=["blog", "reddit"],
        keywords=["machine learning", "AI", "beginners", "tutorial"],
        include_research=True
    )

    print(f"\n✓ Content package generated!\n")

    # Display research
    if package.get("research") and package["research"].success:
        print("--- RESEARCH FINDINGS ---")
        print(package["research"].content[:300] + "...\n")

    # Display content
    for format_name, result in package["content"].items():
        if result.success:
            print(f"\n--- {format_name.upper()} CONTENT ---")
            print(result.content[:300] + "...\n")
            print(f"Metadata: {result.metadata}\n")


def example_custom_workflow():
    """Example: Custom workflow execution."""
    print("\n" + "=" * 60)
    print("Example 4: Custom Workflow")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = ContentOrchestrator()
    session_id = orchestrator.start_session()

    # Execute custom workflow
    print("Executing workflow: research -> blog -> image...")

    results = orchestrator.execute_workflow(
        workflow=["research", "blog_writer"],
        initial_request="The future of quantum computing",
        session_id=session_id,
        context={
            "keywords": ["quantum computing", "future", "technology"]
        }
    )

    print(f"\n✓ Workflow completed!\n")

    # Display results
    for agent_type, result in results.items():
        if result.success:
            print(f"--- {agent_type.upper()} ---")
            print(f"Content length: {len(result.content)} characters")
            print(f"Metadata: {result.metadata}\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("CONTENTBLITZ - PROGRAMMATIC USAGE EXAMPLES")
    print("=" * 60)

    try:
        # Run examples
        example_simple_generation()
        example_with_brand_voice()
        example_content_package()
        example_custom_workflow()

        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        print("\nMake sure you have:")
        print("1. Installed all dependencies: pip install -r requirements.txt")
        print("2. Configured API keys in .env file")
        print("3. Set at least one LLM provider API key")


if __name__ == "__main__":
    main()
