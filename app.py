"""ContentBlitz - Multi-Agent Content Marketing System
Streamlit UI Application
"""
import streamlit as st
from core.orchestrator import ContentOrchestrator
from core.brand_voice import BrandProfile
from utils.seo_analyzer import SEOAnalyzer
import plotly.graph_objects as go
from datetime import datetime
import base64


# Page configuration
st.set_page_config(
    page_title="ContentBlitz - AI Content Marketing",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .success-box {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "generation_history" not in st.session_state:
    st.session_state.generation_history = []

if "last_quick_result" not in st.session_state:
    st.session_state.last_quick_result = None

if "brand_configured" not in st.session_state:
    st.session_state.brand_configured = False

if "content_package" not in st.session_state:
    st.session_state.content_package = None

if "package_topic" not in st.session_state:
    st.session_state.package_topic = None


def initialize_orchestrator():
    """Initialize the content orchestrator."""
    if st.session_state.orchestrator is None:
        with st.spinner("Initializing ContentBlitz..."):
            try:
                orchestrator = ContentOrchestrator(
                    llm_provider=st.session_state.get("llm_provider", "openai")
                )
                st.session_state.orchestrator = orchestrator
                st.success("✓ ContentBlitz initialized successfully!")
            except Exception as e:
                st.error(f"Failed to initialize: {str(e)}")
                st.info("Please ensure you have configured your OPENAI_API_KEY in your .env file")
                return False
    return True


def render_header():
    """Render the application header."""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown('<p class="main-header">⚡ ContentBlitz</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">AI-Powered Multi-Agent Content Marketing System</p>', unsafe_allow_html=True)

    with col2:
        if st.session_state.session_id:
            st.success("Session Active")
        else:
            st.info("No Active Session")


def render_sidebar():
    """Render the sidebar with configuration options."""
    st.sidebar.title("⚙️ Configuration")

    # LLM Provider Selection
    st.sidebar.subheader("LLM Settings")
    llm_provider = st.sidebar.selectbox(
        "Provider",
        ["openai", "anthropic", "google"],
        index=0
    )
    st.session_state.llm_provider = llm_provider

    # Brand Configuration
    st.sidebar.subheader("🎨 Brand Profile")

    with st.sidebar.expander("Configure Brand Voice", expanded=not st.session_state.brand_configured):
        brand_name = st.text_input("Brand Name", value="Your Brand")

        voice_attrs = st.multiselect(
            "Voice Attributes",
            ["Professional", "Friendly", "Authoritative", "Casual", "Technical", "Conversational", "Humorous"],
            default=["Professional", "Friendly"]
        )

        target_audience = st.text_area(
            "Target Audience",
            value="Marketers and content creators",
            height=80
        )

        industry = st.text_input("Industry", value="Marketing")

        tone_guidelines = st.text_area(
            "Tone Guidelines",
            value="Be clear, concise, and actionable. Use examples and data when possible.",
            height=100
        )

        if st.button("Save Brand Profile", type="primary"):
            if initialize_orchestrator():
                profile = BrandProfile(
                    brand_name=brand_name,
                    voice_attributes=[v.lower() for v in voice_attrs],
                    target_audience=target_audience,
                    industry=industry,
                    tone_guidelines=tone_guidelines
                )

                st.session_state.orchestrator.set_brand_profile(profile)
                st.session_state.brand_configured = True
                st.success("✓ Brand profile saved!")

    # Session Management
    st.sidebar.subheader("📊 Session")

    if st.sidebar.button("Start New Session"):
        if initialize_orchestrator():
            session_id = st.session_state.orchestrator.start_session()
            st.session_state.session_id = session_id
            st.sidebar.success(f"Session started!")

    if st.session_state.session_id and st.sidebar.button("End Session"):
        st.session_state.session_id = None
        st.sidebar.info("Session ended")


def render_main_interface():
    """Render the main content generation interface."""
    tabs = st.tabs([
        "🚀 Quick Generate",
        "📦 Content Package",
        "💬 Chat Mode",
        "📈 Analytics"
    ])

    # Tab 1: Quick Generate
    with tabs[0]:
        render_quick_generate()

    # Tab 2: Content Package
    with tabs[1]:
        render_content_package()

    # Tab 3: Chat Mode
    with tabs[2]:
        render_chat_mode()

    # Tab 4: Analytics
    with tabs[3]:
        render_analytics()


def render_quick_generate():
    """Render the quick generate interface."""
    st.subheader("🚀 Quick Content Generation")

    st.write("Generate content quickly with automatic agent routing.")

    request = st.text_area(
        "What would you like to create?",
        placeholder="e.g., 'Write a blog post about AI in marketing' or 'Create a Reddit post about productivity tips'",
        height=100
    )

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        keywords = st.text_input(
            "Target Keywords (comma-separated)",
            placeholder="AI, marketing, automation"
        )

    with col2:
        content_tone = st.selectbox(
            "Tone",
            ["Default", "Professional", "Casual", "Technical", "Friendly"]
        )

    with col3:
        include_seo = st.checkbox("SEO Analysis", value=True)

    if st.button("Generate Content", type="primary", use_container_width=True):
        if not request:
            st.warning("Please enter a content request")
            return

        if not initialize_orchestrator():
            return

        with st.spinner("🤖 AI agents are working on your request..."):
            try:
                context = {}

                if keywords:
                    context["keywords"] = [k.strip() for k in keywords.split(",")]

                if content_tone != "Default":
                    context["tone"] = content_tone.lower()

                result = st.session_state.orchestrator.process_request(
                    request=request,
                    context=context
                )

                st.session_state.generation_history.append(result)
                # Store last result for persistence
                st.session_state.last_quick_result = {
                    "result": result,
                    "request": request
                }

                st.success("✓ Content generated successfully!")

            except Exception as e:
                st.error(f"Generation failed: {str(e)}")
                st.session_state.last_quick_result = None

    # Display stored result (persists across reruns)
    if st.session_state.last_quick_result:
        result = st.session_state.last_quick_result["result"]
        request_text = st.session_state.last_quick_result["request"]

        st.markdown("---")

        # Header with clear button
        col_header, col_button = st.columns([4, 1])
        with col_header:
            st.markdown("### Generated Content")
        with col_button:
            if st.button("Clear Results", type="secondary", key="clear_quick"):
                st.session_state.last_quick_result = None
                st.rerun()

        for agent_type, agent_result in result["results"].items():
            if agent_result.success:
                with st.expander(f"📄 {agent_type.replace('_', ' ').title()}", expanded=True):
                    st.markdown(agent_result.content)

                    # Download button
                    filename = f"{request_text[:30].replace(' ', '_').lower()}_{agent_type}.md"
                    st.download_button(
                        label=f"Download {agent_type.replace('_', ' ').title()}",
                        data=agent_result.content,
                        file_name=filename,
                        mime="text/markdown",
                        key=f"download_quick_{agent_type}"
                    )

                    # Show metadata
                    if agent_result.metadata:
                        st.markdown("---")
                        st.caption("Metadata:")

                        if "seo_score" in agent_result.metadata:
                            score = agent_result.metadata["seo_score"]
                            st.metric("SEO Score", f"{score}/100")

                            if "recommendations" in agent_result.metadata:
                                with st.expander("SEO Recommendations"):
                                    for rec in agent_result.metadata["recommendations"]:
                                        st.write(f"• {rec}")

                        # Display other metadata
                        metadata_cols = st.columns(3)
                        meta_items = list(agent_result.metadata.items())[:6]

                        for i, (key, value) in enumerate(meta_items):
                            if key not in ["seo_score", "recommendations", "sources"]:
                                with metadata_cols[i % 3]:
                                    st.caption(f"**{key}**: {value}")

            else:
                st.error(f"❌ {agent_type} failed: {agent_result.error}")


def render_content_package():
    """Render the content package generator."""
    st.subheader("📦 Complete Content Package")

    st.write("Generate a comprehensive content package with multiple formats.")

    col1, col2 = st.columns([2, 1])

    with col1:
        topic = st.text_input(
            "Content Topic",
            placeholder="e.g., 'The Future of AI in Marketing'"
        )

    with col2:
        include_research = st.checkbox("Include Research", value=True)

    formats = st.multiselect(
        "Select Content Formats",
        ["Blog Post", "Reddit Post", "Social Media", "Image/Visual"],
        default=["Blog Post"]
    )

    keywords_input = st.text_input(
        "Target Keywords (comma-separated)",
        placeholder="AI, marketing, future, trends"
    )

    if st.button("Generate Package", type="primary", use_container_width=True):
        if not topic:
            st.warning("Please enter a topic")
            return

        if not formats:
            st.warning("Please select at least one format")
            return

        if not initialize_orchestrator():
            return

        with st.spinner("🎨 Creating your content package... This may take a few minutes."):
            try:
                format_mapping = {
                    "Blog Post": "blog",
                    "Reddit Post": "reddit",
                    "Social Media": "reddit",
                    "Image/Visual": "image"
                }

                selected_formats = [format_mapping[f] for f in formats]

                kwargs = {
                    "include_research": include_research
                }

                if keywords_input:
                    kwargs["keywords"] = [k.strip() for k in keywords_input.split(",")]

                package = st.session_state.orchestrator.generate_content_package(
                    topic=topic,
                    formats=selected_formats,
                    **kwargs
                )

                # Store in session state to persist across reruns
                st.session_state.content_package = package
                st.session_state.package_topic = topic

                st.success("✓ Content package generated!")

            except Exception as e:
                st.error(f"Package generation failed: {str(e)}")
                st.session_state.content_package = None
                st.session_state.package_topic = None

    # Display stored package (persists across reruns)
    if st.session_state.content_package:
        package = st.session_state.content_package
        topic = st.session_state.package_topic

        st.markdown("---")

        # Header with clear button
        col_header, col_button = st.columns([4, 1])
        with col_header:
            st.markdown("### Generated Content Package")
        with col_button:
            if st.button("Clear Package", type="secondary"):
                st.session_state.content_package = None
                st.session_state.package_topic = None
                st.rerun()

        # Display research
        if package.get("research") and package["research"].success:
            with st.expander("🔍 Research Findings", expanded=False):
                st.markdown(package["research"].content)

        # Display content
        for format_name, result in package["content"].items():
            if result.success:
                with st.expander(f"📄 {format_name.title()}", expanded=True):
                    st.markdown(result.content)

                    # Download button
                    st.download_button(
                        label=f"Download {format_name}",
                        data=result.content,
                        file_name=f"{topic.lower().replace(' ', '_')}_{format_name}.md",
                        mime="text/markdown",
                        key=f"download_{format_name}"  # Unique key for each button
                    )


def render_chat_mode():
    """Render the chat interface."""
    st.subheader("💬 Chat with ContentBlitz")

    st.write("Have a conversation with AI agents to iteratively create and refine content.")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Initialize orchestrator if needed
    if not st.session_state.orchestrator:
        if not initialize_orchestrator():
            st.warning("Please configure ContentBlitz before using chat mode.")
            return

    # Display existing chat messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            try:
                with st.spinner("Thinking..."):
                    result = st.session_state.orchestrator.process_request(user_input)

                    if not result.get("results"):
                        response = "I couldn't generate a response. Please try rephrasing your request."
                    else:
                        response_parts = []
                        for agent_type, agent_result in result["results"].items():
                            if agent_result.success:
                                response_parts.append(f"**{agent_type.replace('_', ' ').title()}:**\n\n{agent_result.content}\n\n")
                            else:
                                response_parts.append(f"**{agent_type.replace('_', ' ').title()}:** ❌ {agent_result.error}\n\n")

                        response = "\n".join(response_parts) if response_parts else "No response generated."

                # Display response
                message_placeholder.markdown(response)

                # Add to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}\n\nPlease check your configuration and try again."
                message_placeholder.error(error_msg)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })

        # Force rerun to show the new messages properly
        st.rerun()


def render_analytics():
    """Render analytics dashboard."""
    st.subheader("📈 Content Analytics")

    if not st.session_state.generation_history:
        st.info("No content generated yet. Generate some content to see analytics!")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Generations",
            len(st.session_state.generation_history)
        )

    with col2:
        agent_usage = {}
        for item in st.session_state.generation_history:
            for agent in item.get("agents_used", []):
                agent_usage[agent] = agent_usage.get(agent, 0) + 1

        st.metric(
            "Most Used Agent",
            max(agent_usage, key=agent_usage.get).title() if agent_usage else "N/A"
        )

    with col3:
        total_content = sum(
            len(result.content)
            for item in st.session_state.generation_history
            for result in item.get("results", {}).values()
            if result.success
        )
        st.metric(
            "Total Content (chars)",
            f"{total_content:,}"
        )

    with col4:
        avg_seo_scores = []
        for item in st.session_state.generation_history:
            for result in item.get("results", {}).values():
                if "seo_score" in result.metadata:
                    avg_seo_scores.append(result.metadata["seo_score"])

        if avg_seo_scores:
            st.metric(
                "Avg SEO Score",
                f"{sum(avg_seo_scores) / len(avg_seo_scores):.1f}/100"
            )
        else:
            st.metric("Avg SEO Score", "N/A")

    # Agent usage chart
    st.markdown("### Agent Usage")

    if agent_usage:
        fig = go.Figure(data=[
            go.Bar(
                x=list(agent_usage.keys()),
                y=list(agent_usage.values()),
                marker_color='#667eea'
            )
        ])

        fig.update_layout(
            xaxis_title="Agent",
            yaxis_title="Number of Uses",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

    # Recent generations
    st.markdown("### Recent Generations")

    for i, item in enumerate(reversed(st.session_state.generation_history[-5:])):
        with st.expander(f"{item['request'][:50]}..." if len(item['request']) > 50 else item['request']):
            st.caption(f"Agents: {', '.join(item['agents_used'])}")

            for agent_type, result in item["results"].items():
                st.markdown(f"**{agent_type}:**")
                st.text(result.content[:200] + "..." if len(result.content) > 200 else result.content)


def main():
    """Main application entry point."""
    render_header()
    render_sidebar()
    render_main_interface()

    # Footer
    st.markdown("---")
    st.caption("ContentBlitz v1.0 - AI-Powered Content Marketing System")


if __name__ == "__main__":
    main()
