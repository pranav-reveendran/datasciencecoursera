# 📈 Equity Research AI

> **Cutting-Edge LLM-Powered Equity Research Tool** | Built with Latest AI Technologies (Nov 2024 - Jan 2025)

A modern, production-ready equity research tool that leverages the latest advancements in Large Language Models, Multi-Agent Systems, and Retrieval-Augmented Generation (RAG) to provide comprehensive stock market analysis.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/🦜-LangChain-green.svg)](https://github.com/langchain-ai/langchain)
[![LangGraph](https://img.shields.io/badge/🕸️-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg?logo=Streamlit&logoColor=white)](https://streamlit.io)

## 🚀 What Makes This Cutting-Edge?

### Latest Technologies (November 2024 - January 2025)

1. **🕸️ Multi-Agent System with LangGraph**
   - State-of-the-art agent orchestration framework
   - Router → Research → Analysis → Synthesis pipeline
   - Replaces traditional single-LLM approaches

2. **🔍 Advanced Hybrid RAG**
   - **Semantic Search**: Dense retrieval using OpenAI embeddings
   - **Keyword Search**: BM25 for precise matching
   - **Reciprocal Rank Fusion (RRF)**: Combines both approaches
   - **Reranking**: Cohere's latest reranking models for relevance

3. **🤖 Modern LLM Integration**
   - Support for GPT-4 Turbo and Claude 3 Opus
   - Function calling for real-time market data
   - Streaming responses for better UX

4. **📊 Real-Time Market Data Tools**
   - Tool-calling agents that fetch live stock prices
   - Financial statements and analyst ratings
   - Company fundamentals and comparisons

5. **📰 Multi-Source News Aggregation**
   - Yahoo Finance, NewsAPI, RSS feeds
   - Automatic content enrichment via web scraping
   - Smart deduplication and ranking

6. **💾 ChromaDB Vector Database**
   - Modern alternative to FAISS
   - Better performance and persistence
   - Optimized for production use

## 📋 Features

- ✅ **Hybrid Search**: Semantic + Keyword retrieval with RRF
- ✅ **Multi-Agent System**: Specialized agents for different tasks
- ✅ **Real-Time Data**: Live stock prices and market metrics
- ✅ **Source Citations**: Full attribution and URLs
- ✅ **Streaming Responses**: Real-time answer generation
- ✅ **Modern UI**: Clean Streamlit interface
- ✅ **Configurable**: Support for multiple LLM providers
- ✅ **Production-Ready**: Proper error handling and logging

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                         │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Multi-Agent System                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │  Router  │ → │ Research │ → │ Analysis │ → │Synthesis ││
│  │  Agent   │   │  Agent   │   │  Agent   │   │  Agent   ││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘│
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────────┐   ┌──────────────┐
│ Hybrid RAG   │    │ News Aggregator  │   │ Market Tools │
│ Retriever    │    │ (Multi-Source)   │   │ (YFinance)   │
├──────────────┤    ├──────────────────┤   ├──────────────┤
│ • Semantic   │    │ • Yahoo Finance  │   │ • Prices     │
│ • BM25       │    │ • NewsAPI        │   │ • Financials │
│ • RRF Fusion │    │ • RSS Feeds      │   │ • Ratings    │
│ • Reranking  │    │ • Web Scraping   │   │ • Compares   │
└──────────────┘    └──────────────────┘   └──────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│              ChromaDB Vector Database                     │
│  (Persistent storage for news embeddings)                │
└──────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Component | Technology | Why? |
|-----------|-----------|------|
| **LLM Orchestration** | LangChain + LangGraph | Latest multi-agent framework |
| **LLM Providers** | OpenAI GPT-4 / Anthropic Claude | Best-in-class models |
| **Vector DB** | ChromaDB | Modern, persistent, fast |
| **Embeddings** | OpenAI text-embedding-3-large | Latest embedding model |
| **Keyword Search** | BM25Okapi | Industry-standard sparse retrieval |
| **Reranking** | Cohere Rerank v3 | State-of-the-art reranking |
| **News Sources** | Yahoo Finance, NewsAPI, RSS | Comprehensive coverage |
| **Market Data** | yfinance, Alpha Vantage | Free, reliable APIs |
| **Web UI** | Streamlit | Rapid prototyping, clean UX |
| **Config Management** | Pydantic + python-dotenv | Type-safe configuration |

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip or conda
- API keys (see below)

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd equity-research-ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API keys**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required API keys:
- **OPENAI_API_KEY** (Required) - Get from [OpenAI Platform](https://platform.openai.com/)
- **COHERE_API_KEY** (Optional, for reranking) - Get from [Cohere](https://cohere.com/)
- **NEWS_API_KEY** (Optional) - Get from [NewsAPI](https://newsapi.org/)
- **ANTHROPIC_API_KEY** (Optional) - Get from [Anthropic](https://www.anthropic.com/)

4. **Run the app**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🎯 Quick Start

1. **Launch the app**:
   ```bash
   streamlit run app.py
   ```

2. **Index news for a stock**:
   - Enter ticker (e.g., `AAPL`) in sidebar
   - Click "Index News"
   - Wait for articles to be fetched and indexed

3. **Ask questions**:
   - "What's the latest news on Apple?"
   - "Compare Tesla and Ford financials"
   - "What are analysts saying about NVIDIA?"
   - "Summarize recent market trends"

4. **Explore results**:
   - View AI-generated analysis
   - Check source citations
   - See real-time market data

## 📚 Example Queries

### Company Research
```
"What's the latest news on Apple?"
"Tell me about Microsoft's recent earnings"
"What are the key risks for Tesla?"
```

### Comparative Analysis
```
"Compare Tesla and Ford"
"Which is better: Amazon or Walmart?"
"Compare big tech stocks (AAPL, GOOGL, MSFT)"
```

### Market Insights
```
"What's happening in the semiconductor sector?"
"Summarize recent AI stock trends"
"What's driving the market today?"
```

### Specific Metrics
```
"What's NVDA's P/E ratio?"
"Show me Apple's financials"
"What are analysts recommending for TSLA?"
```

## ⚙️ Configuration

Edit `.env` to customize:

```bash
# LLM Settings
DEFAULT_LLM_PROVIDER=openai  # or 'anthropic'
DEFAULT_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.1

# RAG Settings
TOP_K_RETRIEVAL=10
RERANK_TOP_N=5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# News Settings
MAX_NEWS_ARTICLES=100
NEWS_LOOKBACK_DAYS=30
```

## 🔧 Advanced Usage

### Custom News Sources

Add your own RSS feeds in `src/data/news_fetcher.py`:

```python
rss_feeds = [
    "https://your-custom-feed.com/rss",
    # Add more feeds
]
```

### Change LLM Provider

Switch to Anthropic Claude:

```python
# In .env
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_MODEL=claude-3-opus-20240229
```

### Adjust Retrieval Parameters

Fine-tune retrieval in `src/utils/config.py`:

```python
class RAGConfig(BaseModel):
    top_k: int = 15  # Retrieve more results
    rerank_top_n: int = 7  # Rerank to top 7
    use_hybrid_search: bool = True
    use_reranking: bool = True
```

## 📊 Project Structure

```
equity-research-ai/
├── app.py                      # Streamlit UI
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
├── README.md                  # This file
│
├── src/
│   ├── agents/
│   │   └── research_agent.py  # Multi-agent system (LangGraph)
│   │
│   ├── retrieval/
│   │   └── hybrid_retriever.py # Hybrid RAG pipeline
│   │
│   ├── data/
│   │   └── news_fetcher.py    # Multi-source news aggregation
│   │
│   ├── tools/
│   │   └── market_tools.py    # Real-time market data tools
│   │
│   └── utils/
│       └── config.py          # Configuration management
│
└── data/
    ├── chroma_db/             # Vector database (auto-created)
    └── raw_articles/          # Cached articles (auto-created)
```

## 🔐 Security & Privacy

- All API keys stored in `.env` (not committed to git)
- Local vector database (data stays on your machine)
- No user data collection
- Configurable data retention

## 🚧 Roadmap

Future enhancements:

- [ ] Support for local LLMs (Ollama, LM Studio)
- [ ] PDF report generation
- [ ] Historical backtesting
- [ ] Portfolio analysis
- [ ] Sentiment analysis dashboard
- [ ] Multi-language support
- [ ] Mobile app
- [ ] API endpoints

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - feel free to use for personal or commercial projects

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [Streamlit](https://streamlit.io) - Web UI
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Cohere](https://cohere.com/) - Reranking
- [OpenAI](https://openai.com/) - LLM & Embeddings

## 📞 Support

Having issues? Check:
1. API keys are set correctly in `.env`
2. Dependencies installed: `pip install -r requirements.txt`
3. Python version is 3.9+

For bugs or features, open an issue on GitHub.

---

## 📝 How to Rename This Repository

Since this repo is currently named `datasciencecoursera`, here's how to rename it:

### Option 1: GitHub Web Interface (Recommended)

1. Go to your repository on GitHub
2. Click **Settings** (near the top right)
3. In the "Repository name" field, enter your new name:
   - Suggested: `equity-research-ai` or `stock-research-ai`
4. Click **Rename**
5. Update your local remote:
   ```bash
   git remote set-url origin https://github.com/YOUR_USERNAME/NEW_REPO_NAME.git
   ```

### Option 2: Command Line

```bash
# Update local remote URL after renaming on GitHub
git remote set-url origin https://github.com/YOUR_USERNAME/equity-research-ai.git

# Verify
git remote -v
```

### Suggested Repository Names

- `equity-research-ai`
- `stock-research-assistant`
- `ai-equity-analyst`
- `market-research-ai`
- `smart-stock-research`

---

**Built with ❤️ using cutting-edge AI technologies**

*Last updated: January 2025*
