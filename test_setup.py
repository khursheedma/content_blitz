"""Quick test script to verify ContentBlitz setup."""

import sys
import os


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from core.orchestrator import ContentOrchestrator
        print("✓ Core modules imported")
    except Exception as e:
        print(f"✗ Failed to import core modules: {e}")
        return False

    try:
        from agents import ResearchAgent, BlogWriterAgent, RedditAgent, ImageAgent
        print("✓ Agent modules imported")
    except Exception as e:
        print(f"✗ Failed to import agents: {e}")
        return False

    try:
        from utils import LLMClient, VectorMemory, SEOAnalyzer
        print("✓ Utility modules imported")
    except Exception as e:
        print(f"✗ Failed to import utilities: {e}")
        return False

    return True


def test_config():
    """Test configuration."""
    print("\nTesting configuration...")

    try:
        from config import Config

        print(f"  Default LLM Provider: {Config.DEFAULT_LLM_PROVIDER}")
        print(f"  Default Model: {Config.DEFAULT_MODEL}")
        print(f"  Temperature: {Config.TEMPERATURE}")

        if Config.OPENAI_API_KEY:
            print(f"✓ OPENAI_API_KEY is configured (length: {len(Config.OPENAI_API_KEY)})")
        else:
            print("✗ OPENAI_API_KEY is not set!")
            print("\n  To fix this:")
            print("  1. Copy .env.example to .env")
            print("  2. Add your OpenAI API key to .env")
            print("  3. Get key from: https://platform.openai.com/api-keys")
            return False

        return True

    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_orchestrator():
    """Test orchestrator initialization."""
    print("\nTesting orchestrator...")

    try:
        from core.orchestrator import ContentOrchestrator

        orch = ContentOrchestrator()
        print(f"✓ Orchestrator initialized")
        print(f"  LLM Provider: {orch.llm_client.provider.value}")
        print(f"  Model: {orch.llm_client.model}")
        print(f"  Available agents: {', '.join(orch.agents.keys())}")

        return True

    except Exception as e:
        print(f"✗ Failed to initialize orchestrator: {e}")
        return False


def test_simple_generation():
    """Test simple content generation."""
    print("\nTesting content generation...")
    print("  (This will make an API call to OpenAI)")

    response = input("  Run generation test? (y/n): ").strip().lower()

    if response != 'y':
        print("  Skipped generation test")
        return True

    try:
        from core.orchestrator import ContentOrchestrator

        orch = ContentOrchestrator()

        print("\n  Generating test content (this may take 10-20 seconds)...")

        result = orch.process_request(
            request="Write a very short 2-sentence introduction about AI",
            context={"tone": "professional"}
        )

        print(f"\n✓ Content generated successfully!")
        print(f"  Agents used: {', '.join(result['agents_used'])}")

        for agent_type, agent_result in result["results"].items():
            if agent_result.success:
                print(f"\n  --- {agent_type.upper()} OUTPUT ---")
                content_preview = agent_result.content[:200]
                print(f"  {content_preview}...")

        return True

    except Exception as e:
        print(f"✗ Generation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("ContentBlitz Setup Test")
    print("=" * 70)

    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Orchestrator", test_orchestrator),
        ("Generation", test_simple_generation),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n🎉 All tests passed! ContentBlitz is ready to use.")
        print("\nNext steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Or run: python example_usage.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Configure API key: cp .env.example .env (then edit)")
        print("  - Check .env file has: OPENAI_API_KEY=sk-...")

    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
