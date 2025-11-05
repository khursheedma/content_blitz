# ContentBlitz - Quick Start Guide

Get ContentBlitz up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key (Get one at: https://platform.openai.com/api-keys)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- OpenAI client for GPT models
- Vector database (ChromaDB)
- Web framework (Streamlit)
- Content analysis tools

```bash
# Download NLTK data for SEO analysis
python setup_nltk.py
```

### 2. Configure API Keys

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```bash
# Required: OpenAI API Key
OPENAI_API_KEY=sk-...
```

**Getting Your OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key and paste it into your `.env` file

### 3. Run ContentBlitz

**Option A: Web Interface (Recommended)**

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

**Option B: Python Script**

```bash
python example_usage.py
```

This runs programmatic examples showing different use cases.

## First Steps in the UI

### 1. Configure Your Brand (Optional but Recommended)

- Open the sidebar (click `>` if collapsed)
- Expand "Configure Brand Voice"
- Fill in:
  - Brand Name
  - Voice Attributes (select multiple)
  - Target Audience
  - Industry
  - Tone Guidelines
- Click "Save Brand Profile"

### 2. Start a Session

- In the sidebar, click "Start New Session"
- You'll see "Session Active" indicator

### 3. Generate Your First Content

**Quick Generate Tab:**
1. Type your request: "Write a blog post about AI in marketing"
2. Add keywords: "AI, marketing, automation"
3. Select tone (optional)
4. Click "Generate Content"
5. Wait 30-60 seconds for AI agents to work

**Content Package Tab:**
1. Enter topic: "The Future of Remote Work"
2. Select formats: Blog Post, Reddit Post, Image
3. Add keywords
4. Check "Include Research"
5. Click "Generate Package"
6. Wait 2-3 minutes for complete package

## Quick Wins

### Generate a Blog Post with SEO

1. Go to Quick Generate
2. Request: "Write a blog post about [YOUR TOPIC]"
3. Add 3-5 target keywords
4. Check "SEO Analysis"
5. Generate!

You'll get:
- Complete blog post with proper structure
- SEO score and recommendations
- Word count and readability metrics

### Create Social Media Content

1. Go to Quick Generate
2. Request: "Create a Reddit post about [TOPIC] for r/[subreddit]"
3. Generate!

You'll get:
- Platform-optimized content
- Engaging title
- Proper formatting

### Research a Topic

1. Go to Quick Generate
2. Request: "Research the latest trends in [TOPIC]"
3. Generate!

You'll get:
- Comprehensive research summary
- Key findings and insights
- Source links

## Common Issues & Solutions

### "Failed to initialize" Error

**Problem**: No valid API key found

**Solution**:
1. Check your `.env` file exists in project root
2. Verify API key is correctly formatted
3. Ensure no extra spaces around the key
4. Test API key on provider's website

### "Module not found" Error

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

### Slow Generation

**Normal**: First generation takes longer (loading models)

**Tip**: Subsequent generations are faster (memory/cache)

### ChromaDB Errors

**Solution**: Delete the database and restart:
```bash
rm -rf chroma_db/
streamlit run app.py
```

## Pro Tips

1. **Use Keywords**: Always add 3-5 target keywords for better SEO
2. **Brand Voice**: Configure once, use everywhere
3. **Content Package**: For comprehensive deliverables
4. **Chat Mode**: For iterative refinement
5. **Save Results**: Use download buttons in Content Package

## Next Steps

- **Customize**: Adjust brand voice to your needs
- **Experiment**: Try different content types and formats
- **Iterate**: Use Chat Mode to refine content
- **Scale**: Generate multiple pieces quickly

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review [example_usage.py](example_usage.py) for code examples
- Open an issue on GitHub for bugs or questions

---

**Ready to blitz your content creation? Start generating now!** ⚡
