# ⚡ ContentBlitz

**AI-Powered Multi-Agent Content Marketing System**

ContentBlitz is an intelligent content marketing assistant that automates research, writing, and optimization to deliver timely, tailored, platform-ready content at scale.

## 🎯 Features

### Core Capabilities

- **🔍 Research Agent**: Conducts comprehensive web research, gathers statistics, trends, and market insights
- **✍️ Blog Writing Agent**: Creates SEO-optimized, long-form blog posts with proper structure and keyword optimization
- **💬 Reddit Post Agent**: Generates authentic, engaging Reddit posts optimized for specific subreddits
- **🎨 Image Agent**: Creates image prompts and generates visual content for blogs and social media

### Advanced Features

- **🧠 Intelligent Query Routing**: Automatically routes requests to appropriate agents based on intent
- **💾 Conversation Memory**: ChromaDB-powered vector memory for context-aware multi-turn conversations
- **🎭 Brand Voice Management**: Maintain consistent brand voice across all content types
- **📊 SEO Analysis**: Real-time SEO scoring with actionable recommendations
- **📈 Content Performance Scoring**: Quality assessment for blogs and social content
- **🎯 Multi-Format Content Packages**: Generate complete content packages with research, blog, social, and visuals
- **💬 Interactive Chat Mode**: Conversational interface for iterative content creation

## 🏗️ Architecture

```
content_blitz/
├── agents/              # Specialized content generation agents
│   ├── base_agent.py
│   ├── research_agent.py
│   ├── blog_writer_agent.py
│   ├── reddit_agent.py
│   └── image_agent.py
├── core/                # Core orchestration logic
│   ├── orchestrator.py
│   ├── query_router.py
│   ├── memory.py
│   └── brand_voice.py
├── utils/               # Utility modules
│   ├── llm_client.py
│   ├── vector_db.py
│   ├── seo_analyzer.py
│   └── content_scorer.py
├── app.py               # Streamlit UI
├── config.py            # Configuration management
└── requirements.txt     # Dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (Get one at: https://platform.openai.com/api-keys)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd content_blitz
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

```bash
# Download NLTK data for SEO keyword analysis
python setup_nltk.py
```

4. **Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
# Required: OpenAI API Key
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Optional: For enhanced research
SERPAPI_API_KEY=your_serpapi_key_here

# Optional: For AI image generation
STABILITY_API_KEY=your_stability_ai_key_here

# OpenAI Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4o
```

5. **Run the application**

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Quick Generate

Generate content with automatic agent routing:

1. Navigate to **Quick Generate** tab
2. Enter your content request (e.g., "Write a blog post about AI in marketing")
3. Optionally add target keywords and select tone
4. Click **Generate Content**

The system will automatically route your request to the appropriate agents and generate content.

### Content Package

Create comprehensive content packages:

1. Navigate to **Content Package** tab
2. Enter your topic
3. Select formats (Blog Post, Reddit Post, Social Media, Image)
4. Add target keywords
5. Click **Generate Package**

You'll receive a complete package with research, content in multiple formats, and downloadable files.

### Chat Mode

Have interactive conversations with AI agents:

1. Navigate to **Chat Mode** tab
2. Start chatting with the system
3. Request content creation, refinements, or ask questions
4. Build on previous responses for iterative improvement

### Brand Configuration

Set up your brand voice:

1. Open the sidebar
2. Expand **Configure Brand Voice**
3. Enter brand details:
   - Brand Name
   - Voice Attributes (professional, friendly, etc.)
   - Target Audience
   - Industry
   - Tone Guidelines
4. Click **Save Brand Profile**

All generated content will follow your brand voice guidelines.

## 🔧 Configuration

### LLM Providers

ContentBlitz is configured to use OpenAI GPT models:

- **OpenAI GPT** (Default)
  - Models: gpt-4o (default), gpt-4-turbo, gpt-4, gpt-3.5-turbo
  - Best for: High-quality content generation, fast response times, versatile tasks
  - Get API key: https://platform.openai.com/api-keys

**Note:** The codebase also supports Anthropic Claude and Google Gemini, but requires OpenAI by default.

### Search APIs

For enhanced research capabilities:

- **SERP API** (Recommended): Real-time Google search results
- **DuckDuckGo** (Free fallback): No API key required

### Vector Database

- **ChromaDB**: Used for conversation memory and context storage
- Automatically creates `./chroma_db` directory
- No additional configuration needed

## 💡 Use Cases

### Content Marketing Teams

- **Blog Production**: Generate SEO-optimized blog posts at scale
- **Social Media**: Create platform-specific content (Reddit, LinkedIn, Twitter)
- **Content Calendars**: Batch-generate content packages for multiple channels
- **Brand Consistency**: Maintain voice across all content types

### Solo Creators

- **Research Assistance**: Gather data and insights quickly
- **Content Ideation**: Brainstorm and develop content ideas
- **Multi-Format Publishing**: Create blog + social + visuals from one topic
- **SEO Optimization**: Built-in SEO analysis and recommendations

### Agencies

- **Client Management**: Separate brand profiles per client
- **Content Packages**: Deliver comprehensive content deliverables
- **Quality Assurance**: Performance scoring for all content
- **Scalability**: Handle multiple projects simultaneously

## 🎓 Advanced Features

### Multi-Agent Workflows

Execute custom workflows:

```python
from core.orchestrator import ContentOrchestrator

orchestrator = ContentOrchestrator()
session_id = orchestrator.start_session()

# Execute custom workflow
results = orchestrator.execute_workflow(
    workflow=["research", "blog_writer", "image"],
    initial_request="AI trends in 2024",
    session_id=session_id
)
```

### Programmatic Usage

Use ContentBlitz programmatically:

```python
from core.orchestrator import ContentOrchestrator
from core.brand_voice import BrandProfile

# Initialize
orchestrator = ContentOrchestrator(llm_provider="anthropic")

# Create brand profile
brand = BrandProfile(
    brand_name="TechCorp",
    voice_attributes=["professional", "technical", "innovative"],
    target_audience="developers and tech leaders",
    industry="technology",
    tone_guidelines="Clear, technical, but accessible"
)

# Set brand profile
orchestrator.set_brand_profile(brand)

# Generate content
result = orchestrator.process_request(
    request="Write a technical blog about microservices",
    context={"keywords": ["microservices", "architecture", "scalability"]}
)

# Access results
for agent_type, agent_result in result["results"].items():
    print(f"{agent_type}: {agent_result.content}")
```

### Custom Agents

Extend with custom agents:

```python
from agents.base_agent import BaseAgent, AgentResult

class CustomAgent(BaseAgent):
    @property
    def agent_type(self) -> str:
        return "custom"

    @property
    def description(self) -> str:
        return "My custom agent description"

    def execute(self, task: str, context=None) -> AgentResult:
        # Your custom logic here
        return AgentResult(
            agent_type=self.agent_type,
            content="Generated content",
            success=True
        )
```

## 📊 Performance Metrics

### SEO Scoring

- Word count optimization
- Readability analysis (Flesch Reading Ease)
- Keyword density calculation
- Heading structure analysis
- Automated recommendations

### Content Quality Scoring

**Blog Posts:**
- SEO Score (30%)
- Readability (25%)
- Structure (20%)
- Engagement (15%)
- Length (10%)

**Social Media:**
- Engagement (40%)
- Authenticity (30%)
- Formatting (20%)
- Length (10%)

## 🛠️ Troubleshooting

### Common Issues

**"Failed to initialize" error**
- Ensure at least one LLM API key is configured in `.env`
- Check API key validity
- Verify internet connection

**ChromaDB errors**
- Delete `./chroma_db` directory and restart
- Ensure write permissions in project directory

**Search results not appearing**
- Add SERPAPI_API_KEY for better results
- Falls back to DuckDuckGo if no API key

**Content quality issues**
- Configure brand voice profile
- Provide more detailed context
- Add target keywords
- Try different LLM providers

## 🔐 Security & Privacy

- API keys stored locally in `.env` (never committed)
- Vector database stored locally
- No data sent to third parties except LLM providers
- Conversation history stored locally in ChromaDB

## 🗺️ Roadmap

- [ ] CMS Integration (WordPress, Medium, Ghost)
- [ ] Multi-language support
- [ ] Content calendar scheduling
- [ ] A/B testing for content variations
- [ ] Analytics dashboard with historical trends
- [ ] Export to various formats (PDF, DOCX, HTML)
- [ ] Team collaboration features
- [ ] API endpoints for integrations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built with:
- [Anthropic Claude](https://www.anthropic.com/)
- [OpenAI GPT](https://openai.com/)
- [Streamlit](https://streamlit.io/)
- [ChromaDB](https://www.trychroma.com/)
- [LangChain](https://www.langchain.com/)

## 📧 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting guide

---

**ContentBlitz v1.0** - Automating content creation at scale 🚀
