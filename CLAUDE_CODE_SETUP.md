# Running ContentBlitz in Claude Code

This guide shows you how to set up and run ContentBlitz in the Claude Code environment.

## Quick Start

### Step 1: Set Up Your OpenAI API Key

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Then edit the `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

**Get your OpenAI API key:**
- Go to: https://platform.openai.com/api-keys
- Sign in or create an account
- Click "Create new secret key"
- Copy the key and paste it in your `.env` file

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages. It may take 2-3 minutes.

### Step 3: Run the Application

**Option A: Streamlit Web UI (Recommended)**

```bash
streamlit run app.py
```

The Streamlit app will start and provide a URL. In Claude Code, you can:
- Click the URL to open in your browser
- Or use the forwarded port to access the app

**Option B: Programmatic Usage**

Run the example script to see ContentBlitz in action:

```bash
python example_usage.py
```

This will run several examples showing different use cases.

### Step 4: Use ContentBlitz

Once the Streamlit app is running:

1. **Configure Your Brand** (optional but recommended)
   - Open the sidebar (⚙️ Configuration)
   - Expand "Configure Brand Voice"
   - Fill in your brand details
   - Click "Save Brand Profile"

2. **Start a Session**
   - In the sidebar, click "Start New Session"

3. **Generate Content**
   - Go to "Quick Generate" tab
   - Enter your request (e.g., "Write a blog post about AI in marketing")
   - Add keywords (optional)
   - Click "Generate Content"

## Python Usage Examples

### Example 1: Simple Content Generation

Create a Python file or use the Python console:

```python
from core.orchestrator import ContentOrchestrator

# Initialize
orchestrator = ContentOrchestrator()

# Start session
session_id = orchestrator.start_session()

# Generate content
result = orchestrator.process_request(
    request="Write a short blog post about productivity tips",
    context={"keywords": ["productivity", "tips", "efficiency"]}
)

# Access results
for agent_type, agent_result in result["results"].items():
    if agent_result.success:
        print(f"\n=== {agent_type.upper()} ===")
        print(agent_result.content)
```

### Example 2: Generate Content Package

```python
from core.orchestrator import ContentOrchestrator

orchestrator = ContentOrchestrator()

# Generate complete package
package = orchestrator.generate_content_package(
    topic="The Future of AI",
    formats=["blog", "reddit"],
    keywords=["AI", "technology", "future"],
    include_research=True
)

# Access research
if package["research"].success:
    print("Research:", package["research"].content[:500])

# Access blog
if "blog" in package["content"]:
    print("\nBlog:", package["content"]["blog"].content)
```

### Example 3: With Brand Voice

```python
from core.orchestrator import ContentOrchestrator
from core.brand_voice import BrandProfile

# Create brand profile
brand = BrandProfile(
    brand_name="TechCorp",
    voice_attributes=["professional", "innovative"],
    target_audience="developers and tech leaders",
    industry="technology",
    tone_guidelines="Clear, technical, but accessible"
)

# Initialize with brand
orchestrator = ContentOrchestrator()
orchestrator.set_brand_profile(brand)

# Generate content
result = orchestrator.process_request(
    "Create a blog post about cloud computing"
)
```

## Troubleshooting

### ModuleNotFoundError

If you get `ModuleNotFoundError: No module named 'dotenv'` or similar:

```bash
pip install -r requirements.txt
```

### OPENAI_API_KEY not configured

If you see "OPENAI_API_KEY must be configured":

1. Check that `.env` file exists in the project root
2. Verify the file contains: `OPENAI_API_KEY=sk-...`
3. Make sure there are no extra spaces around the `=`
4. Restart your Python session or Streamlit app

### ChromaDB Errors

If you get ChromaDB errors:

```bash
rm -rf chroma_db/
```

Then restart the application.

### Streamlit Port Already in Use

If port 8501 is already in use:

```bash
streamlit run app.py --server.port 8502
```

## Testing the Setup

Quick test to verify everything works:

```bash
python -c "
from core.orchestrator import ContentOrchestrator
orch = ContentOrchestrator()
print('✓ ContentBlitz initialized successfully!')
print(f'✓ Using provider: {orch.llm_client.provider.value}')
print(f'✓ Using model: {orch.llm_client.model}')
"
```

If this runs without errors, you're all set!

## Working in Claude Code

### Running Background Processes

When running Streamlit in Claude Code:

```bash
# Start in background
streamlit run app.py &

# Or use nohup to keep it running
nohup streamlit run app.py > streamlit.log 2>&1 &
```

### Port Forwarding

Claude Code will automatically forward the Streamlit port (8501). Look for the forwarded URL in the output.

### Viewing Logs

```bash
# View Streamlit logs
tail -f streamlit.log

# Or run in foreground to see logs directly
streamlit run app.py
```

## Next Steps

Once you have ContentBlitz running:

1. Try the **Quick Generate** tab for simple requests
2. Use **Content Package** for comprehensive deliverables
3. Experiment with **Chat Mode** for iterative content creation
4. Check the **Analytics** tab to see your usage stats

## Support

- Check the main [README.md](README.md) for detailed documentation
- Review [QUICKSTART.md](QUICKSTART.md) for setup help
- Run `python example_usage.py` for working code examples

---

**Happy content creating with ContentBlitz!** ⚡
