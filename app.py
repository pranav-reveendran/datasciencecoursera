"""
Streamlit UI for Equity News Research Tool
Modern interface with streaming, chat history, and real-time updates
"""
import streamlit as st
import asyncio
from datetime import datetime
from typing import List
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.utils.config import config
from src.data.news_fetcher import NewsAggregator
from src.retrieval.hybrid_retriever import HybridRetriever
from src.agents.research_agent import EquityResearchSystem

# Page config
st.set_page_config(
    page_title="Equity Research AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern look
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #666;
        font-size: 1.2rem;
        margin-top: 0;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #1f77b4;
        margin: 5px 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "research_system" not in st.session_state:
    st.session_state.research_system = None
if "indexed_tickers" not in st.session_state:
    st.session_state.indexed_tickers = set()


def initialize_system():
    """Initialize the research system"""
    if st.session_state.retriever is None:
        with st.spinner("Initializing AI Research System..."):
            st.session_state.retriever = HybridRetriever()
            st.session_state.research_system = EquityResearchSystem(
                st.session_state.retriever
            )
        st.success("✅ System initialized!")


def index_news(ticker: str, days: int = 30):
    """Index news for a specific ticker"""
    if not config.api_keys.openai:
        st.error("⚠️ Please set OPENAI_API_KEY in .env file")
        return

    with st.spinner(f"Fetching and indexing news for {ticker}..."):
        news_agg = NewsAggregator()
        articles = news_agg.fetch_news_for_ticker(ticker, days)

        if articles:
            num_chunks = st.session_state.retriever.ingest_articles(articles)
            st.session_state.indexed_tickers.add(ticker)
            st.success(
                f"✅ Indexed {len(articles)} articles ({num_chunks} chunks) for {ticker}"
            )
        else:
            st.warning(f"⚠️ No articles found for {ticker}")


def display_sources(sources):
    """Display source citations"""
    if sources:
        with st.expander(f"📚 Sources ({len(sources)})"):
            for idx, source in enumerate(sources, 1):
                st.markdown(f"""
                <div class="source-box">
                    <strong>{idx}. [{source.source}]</strong> - {source.ticker}
                    (Score: {source.score:.3f}, Method: {source.retrieval_method})<br>
                    <small>{source.published_at[:10]}</small><br>
                    <a href="{source.url}" target="_blank">Read more →</a>
                </div>
                """, unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Equity Research AI</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Cutting-edge LLM-powered equity research with multi-agent RAG system</p>',
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API Key status
        st.subheader("API Status")
        api_status = {
            "OpenAI": "✅" if config.api_keys.openai else "❌",
            "Cohere": "✅" if config.api_keys.cohere else "⚠️ Optional",
            "NewsAPI": "✅" if config.api_keys.news_api else "⚠️ Optional",
        }
        for api, status in api_status.items():
            st.text(f"{api}: {status}")

        st.markdown("---")

        # News Indexing
        st.subheader("📰 Index News")
        ticker_input = st.text_input("Stock Ticker", placeholder="e.g., AAPL").upper()
        days_back = st.slider("Days to look back", 7, 90, 30)

        if st.button("Index News", use_container_width=True):
            if ticker_input:
                initialize_system()
                index_news(ticker_input, days_back)
            else:
                st.error("Please enter a ticker symbol")

        # Display indexed tickers
        if st.session_state.indexed_tickers:
            st.info(f"Indexed: {', '.join(st.session_state.indexed_tickers)}")

        st.markdown("---")

        # System Stats
        if st.session_state.retriever:
            st.subheader("📊 System Stats")
            stats = st.session_state.retriever.get_collection_stats()
            st.metric("Total Chunks", stats["total_chunks"])
            st.metric("Hybrid Search", "✅" if stats["has_bm25"] else "❌")

        st.markdown("---")

        # Settings
        st.subheader("🔧 Settings")
        use_reranking = st.checkbox(
            "Use Reranking",
            value=config.rag.use_reranking,
            help="Requires Cohere API key"
        )
        top_k = st.slider("Retrieval Top-K", 3, 20, config.rag.top_k)

        st.markdown("---")

        # Clear chat
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # Main chat interface
    initialize_system()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                display_sources(message["sources"])

    # Chat input
    if prompt := st.chat_input("Ask about stocks, markets, or companies..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                # Extract ticker if mentioned (simple approach)
                ticker = None
                for word in prompt.upper().split():
                    if word in st.session_state.indexed_tickers:
                        ticker = word
                        break

                # Run research
                result = st.session_state.research_system.research(
                    query=prompt,
                    ticker=ticker
                )

                # Display response
                st.markdown(result["response"])

                # Display sources
                if result["sources"]:
                    display_sources(result["sources"])

                # Display market data if available
                if result["market_data"]:
                    with st.expander("📊 Market Data"):
                        st.json(result["market_data"])

        # Save assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "sources": result["sources"],
            "market_data": result["market_data"],
        })

    # Welcome message
    if not st.session_state.messages:
        st.info("""
        👋 Welcome to Equity Research AI!

        **Get Started:**
        1. Enter API keys in `.env` file (see `.env.example`)
        2. Index news for stocks you want to research (use sidebar)
        3. Ask questions about stocks, markets, or companies

        **Example Questions:**
        - "What's the latest news on Apple?"
        - "Compare Tesla and Ford"
        - "What are analysts saying about NVDA?"
        - "Summarize recent market trends"

        **Features:**
        - 🔍 Hybrid Search (Semantic + Keyword)
        - 🤖 Multi-Agent AI System
        - 📈 Real-time Market Data
        - 📰 Multi-source News Aggregation
        - 🎯 Source Citations
        """)


if __name__ == "__main__":
    main()
