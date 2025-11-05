# 🚀 Running ContentBlitz in Claude Code

**Step-by-step guide to execute ContentBlitz right here in Claude Code.**

## ⚡ Quick Execution (3 Steps)

### Step 1: Create `.env` File

```bash
cp .env.example .env
```

Then edit the `.env` file and add your OpenAI API key:

```bash
# Open in editor
nano .env

# Or use echo (replace with your actual key)
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
```

**Get your OpenAI API key:** https://platform.openai.com/api-keys

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages (~2-3 minutes).

```bash
# Download NLTK data for SEO analysis
python setup_nltk.py
```

### Step 3: Run the Application

**Option A: Web UI**

```bash
streamlit run app.py
```

Click the URL that appears (usually http://localhost:8501)

**Option B: Test Script**

```bash
python test_setup.py
```

This verifies everything is working.

**Option C: Example Usage**

```bash
python example_usage.py
```

Runs programmatic examples showing all features.

---

## 📋 Detailed Instructions

### Complete Setup Process

1. **Navigate to project directory**
   ```bash
   cd /home/user/content_blitz
   ```

2. **Create and configure .env file**
   ```bash
   # Copy example
   cp .env.example .env
   
   # Edit with nano
   nano .env
   
   # Add your key (press Ctrl+X, then Y to save):
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Wait for installation to complete. You should see "Successfully installed..."

4. **Verify setup**
   ```bash
   python test_setup.py
   ```
   
   This runs tests to ensure everything is configured correctly.

5. **Run the application**
   
   **For Streamlit UI:**
   ```bash
   streamlit run app.py
   ```
   
   Look for output like:
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8501
   Network URL: http://xxx.xxx.xxx.xxx:8501
   ```
   
   Click the URL to open in your browser.

---

## 💻 Using ContentBlitz Programmatically

### Quick Test

```bash
python << 'PYTHON_EOF'
from core.orchestrator import ContentOrchestrator

# Initialize
orchestrator = ContentOrchestrator()
print("✓ ContentBlitz initialized!")

# Generate content
result = orchestrator.process_request(
    "Write a 3-sentence summary about AI in marketing"
)

# Display results
for agent_type, agent_result in result["results"].items():
    if agent_result.success:
        print(f"\n{agent_type.upper()}:")
        print(agent_result.content[:300] + "...")
PYTHON_EOF
```

### Create Custom Script

```bash
# Create a new script
cat > my_content_generation.py << 'PYTHON_EOF'
from core.orchestrator import ContentOrchestrator

# Initialize
orchestrator = ContentOrchestrator()

# Start session
session_id = orchestrator.start_session()
print(f"Session started: {session_id}")

# Generate blog post
print("\nGenerating blog post...")
result = orchestrator.process_request(
    request="Write a blog post about productivity tips for remote workers",
    context={
        "keywords": ["productivity", "remote work", "tips"],
        "tone": "professional"
    }
)

# Show results
for agent_type, agent_result in result["results"].items():
    if agent_result.success:
        print(f"\n{'='*60}")
        print(f"{agent_type.upper()} RESULT")
        print('='*60)
        print(agent_result.content)
        
        # Show metadata
        if agent_result.metadata:
            print(f"\nMetadata: {agent_result.metadata}")
PYTHON_EOF

# Run it
python my_content_generation.py
```

---

## 🎯 Common Use Cases

### 1. Generate a Blog Post

```bash
python << 'EOF'
from core.orchestrator import ContentOrchestrator

orch = ContentOrchestrator()
result = orch.process_request(
    "Write a blog post about the benefits of AI automation",
    context={"keywords": ["AI", "automation", "benefits", "business"]}
)

for agent_type, agent_result in result["results"].items():
    if agent_result.success and agent_type == "blog_writer":
        print(agent_result.content)
