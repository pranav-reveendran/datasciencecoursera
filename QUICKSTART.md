# 🚀 Quick Start Guide

Get up and running with Equity Research AI in 5 minutes!

## 1️⃣ Prerequisites Check

Before starting, make sure you have:

- ✅ Python 3.9 or higher installed
- ✅ Git installed
- ✅ OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

Check Python version:
```bash
python3 --version  # Should show 3.9 or higher
```

## 2️⃣ Installation (2 minutes)

### Option A: Automated Setup (Recommended)

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh
```

### Option B: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

## 3️⃣ Configure API Keys (1 minute)

Edit the `.env` file:

```bash
# Open .env in your favorite editor
nano .env  # or vim, code, etc.
```

**Minimum required:**
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

**Optional (for enhanced features):**
```bash
COHERE_API_KEY=your-cohere-key  # For reranking
NEWS_API_KEY=your-newsapi-key   # For more news sources
```

## 4️⃣ Launch the App (30 seconds)

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run Streamlit
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 5️⃣ First Research Query (1 minute)

1. **Index some news:**
   - In the sidebar, enter a ticker (e.g., `AAPL`)
   - Click "Index News"
   - Wait 10-30 seconds for articles to be fetched

2. **Ask a question:**
   - In the chat input: "What's the latest news on Apple?"
   - Press Enter
   - Watch the AI research and respond!

## 🎯 Example Queries to Try

```
"What's the latest news on Tesla?"
"Compare Microsoft and Google"
"What are analysts saying about NVIDIA?"
"Tell me about Amazon's recent performance"
"What's happening in the AI sector?"
```

## 🔧 Troubleshooting

### Issue: "No module named 'streamlit'"
**Solution:** Activate virtual environment first:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Issue: "OpenAI API key not found"
**Solution:** Make sure `.env` file exists and has:
```bash
OPENAI_API_KEY=sk-your-actual-key
```

### Issue: "Rate limit exceeded"
**Solution:** You've hit OpenAI API limits. Wait a minute or upgrade your plan.

### Issue: "No articles found"
**Solution:**
- Check your internet connection
- Try a different ticker
- Make sure the ticker is valid (e.g., AAPL, GOOGL, MSFT)

## 📊 Understanding the Results

When you ask a question, the system:

1. **🔍 Retrieves** relevant news from the indexed articles
2. **📊 Fetches** real-time market data (if ticker mentioned)
3. **🤖 Analyzes** using multiple AI agents
4. **📝 Synthesizes** a comprehensive response
5. **📚 Cites** all sources used

## ⚡ Performance Tips

- **Index multiple stocks** before starting your research
- **Use specific tickers** in your questions for better results
- **Enable reranking** (with Cohere API) for more relevant results
- **Adjust Top-K** in sidebar if you want more/fewer sources

## 🎓 Learning Path

1. **Beginner:** Ask simple questions about single stocks
2. **Intermediate:** Compare multiple stocks, ask about sectors
3. **Advanced:** Custom configurations, add news sources, modify agents

## 🆘 Need Help?

- 📖 Read the full [README.md](README.md)
- 🐛 Found a bug? Open an issue on GitHub
- 💡 Have ideas? Contributions welcome!

## 🎉 You're Ready!

You now have a cutting-edge AI-powered equity research tool at your fingertips!

**Pro tip:** Bookmark `http://localhost:8501` for quick access

---

*Happy researching! 📈🤖*
