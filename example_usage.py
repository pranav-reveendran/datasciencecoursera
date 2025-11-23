"""
Example usage of the Equity Research AI system
Demonstrates how to use the components programmatically (without Streamlit UI)
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.utils.config import config
from src.data.news_fetcher import NewsAggregator
from src.retrieval.hybrid_retriever import HybridRetriever
from src.agents.research_agent import EquityResearchSystem


def example_1_basic_research():
    """Example 1: Basic stock research"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Stock Research")
    print("=" * 80)

    # Initialize components
    news_agg = NewsAggregator()
    retriever = HybridRetriever()
    research_system = EquityResearchSystem(retriever)

    # Fetch and index news for Apple
    print("\n1. Fetching news for AAPL...")
    articles = news_agg.fetch_news_for_ticker("AAPL", days_back=30)
    print(f"   Found {len(articles)} articles")

    print("\n2. Indexing articles...")
    num_chunks = retriever.ingest_articles(articles)
    print(f"   Indexed {num_chunks} chunks")

    # Ask a question
    print("\n3. Running research query...")
    question = "What's the latest news about Apple?"

    result = research_system.research(query=question, ticker="AAPL")

    print("\n" + "=" * 80)
    print("RESPONSE:")
    print("=" * 80)
    print(result["response"])

    print("\n" + "=" * 80)
    print("SOURCES:")
    print("=" * 80)
    for idx, source in enumerate(result["sources"][:5], 1):
        print(f"\n{idx}. [{source.source}] - Score: {source.score:.3f}")
        print(f"   {source.content[:150]}...")
        print(f"   URL: {source.url}")


def example_2_comparative_analysis():
    """Example 2: Compare multiple stocks"""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 2: Comparative Analysis")
    print("=" * 80)

    news_agg = NewsAggregator()
    retriever = HybridRetriever()
    research_system = EquityResearchSystem(retriever)

    # Index news for multiple stocks
    tickers = ["TSLA", "F"]  # Tesla vs Ford

    print(f"\n1. Indexing news for {', '.join(tickers)}...")
    for ticker in tickers:
        print(f"\n   Fetching {ticker}...")
        articles = news_agg.fetch_news_for_ticker(ticker, days_back=30)
        retriever.ingest_articles(articles)
        print(f"   ✓ {ticker}: {len(articles)} articles")

    # Compare
    print("\n2. Running comparative analysis...")
    question = "Compare Tesla and Ford. Which one is performing better?"

    result = research_system.research(query=question)

    print("\n" + "=" * 80)
    print("COMPARISON ANALYSIS:")
    print("=" * 80)
    print(result["response"])


def example_3_market_data_integration():
    """Example 3: Use real-time market data"""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 3: Real-Time Market Data")
    print("=" * 80)

    from src.tools.market_tools import (
        get_stock_price,
        get_company_info,
        get_analyst_recommendations,
    )

    ticker = "NVDA"  # NVIDIA

    print(f"\n1. Fetching real-time data for {ticker}...")

    # Get current price
    price_data = get_stock_price.invoke({"ticker": ticker})
    print(f"\n   Current Price: ${price_data.get('current_price', 'N/A')}")
    print(f"   Market Cap: ${price_data.get('market_cap', 0):,}")
    print(f"   P/E Ratio: {price_data.get('pe_ratio', 'N/A')}")

    # Get company info
    company_info = get_company_info.invoke({"ticker": ticker})
    print(f"\n   Company: {company_info.get('name', 'N/A')}")
    print(f"   Sector: {company_info.get('sector', 'N/A')}")
    print(f"   Industry: {company_info.get('industry', 'N/A')}")

    # Get analyst recommendations
    recommendations = get_analyst_recommendations.invoke({"ticker": ticker})
    print(f"\n   Analyst Target: ${recommendations.get('target_mean_price', 'N/A')}")
    print(f"   Recommendation: {recommendations.get('recommendation', 'N/A')}")


def example_4_hybrid_retrieval():
    """Example 4: Demonstrate hybrid search"""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 4: Hybrid Search Demonstration")
    print("=" * 80)

    news_agg = NewsAggregator()
    retriever = HybridRetriever()

    # Index news
    print("\n1. Indexing news about tech stocks...")
    for ticker in ["AAPL", "GOOGL", "MSFT"]:
        articles = news_agg.fetch_news_for_ticker(ticker, days_back=15)
        retriever.ingest_articles(articles)
        print(f"   ✓ {ticker}")

    # Perform hybrid search
    print("\n2. Performing hybrid search...")
    query = "artificial intelligence and cloud computing"

    results = retriever.retrieve(query, top_k=5)

    print(f"\n   Found {len(results)} results using hybrid search")
    print("\n   Top Results:")
    for idx, result in enumerate(results, 1):
        print(f"\n   {idx}. Score: {result.score:.3f} | Method: {result.retrieval_method}")
        print(f"      Source: {result.source}")
        print(f"      {result.content[:100]}...")


def example_5_custom_configuration():
    """Example 5: Custom configuration"""
    print("\n\n" + "=" * 80)
    print("EXAMPLE 5: Custom Configuration")
    print("=" * 80)

    # Show current config
    print("\nCurrent Configuration:")
    print(f"   LLM Provider: {config.llm.provider}")
    print(f"   Model: {config.llm.model}")
    print(f"   Temperature: {config.llm.temperature}")
    print(f"   Top-K Retrieval: {config.rag.top_k}")
    print(f"   Rerank Top-N: {config.rag.rerank_top_n}")
    print(f"   Hybrid Search: {config.rag.use_hybrid_search}")
    print(f"   Reranking: {config.rag.use_reranking}")

    # You can modify config at runtime
    config.rag.top_k = 15  # Retrieve more results
    config.llm.temperature = 0.0  # More deterministic responses

    print("\n✓ Configuration can be modified at runtime!")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print(" " * 20 + "EQUITY RESEARCH AI - EXAMPLES")
    print("=" * 80)

    # Check if API key is set
    if not config.api_keys.openai:
        print("\n❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("   Please create .env file and add your OpenAI API key")
        return

    print("\n✅ API Key found. Starting examples...\n")

    # Run examples
    try:
        # Example 1: Basic research (requires API calls)
        # Uncomment to run:
        # example_1_basic_research()

        # Example 2: Comparative analysis
        # Uncomment to run:
        # example_2_comparative_analysis()

        # Example 3: Market data (free, no OpenAI needed)
        example_3_market_data_integration()

        # Example 4: Hybrid retrieval
        # Uncomment to run:
        # example_4_hybrid_retrieval()

        # Example 5: Configuration
        example_5_custom_configuration()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n\n" + "=" * 80)
    print("Examples complete! Check the output above.")
    print("=" * 80)
    print("\nTo run the full UI: streamlit run app.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
