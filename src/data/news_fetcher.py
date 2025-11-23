"""
Multi-source news fetcher for equity research
Supports: NewsAPI, web scraping, RSS feeds, and financial data APIs
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from newsapi import NewsApiClient
import yfinance as yf
import feedparser
from bs4 import BeautifulSoup
from dataclasses import dataclass
from ..utils.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Structured news article"""
    title: str
    content: str
    source: str
    url: str
    published_at: datetime
    ticker: Optional[str] = None
    sentiment: Optional[float] = None
    metadata: Optional[Dict] = None


class NewsAggregator:
    """
    Modern news aggregator with multiple sources
    Features:
    - NewsAPI for general financial news
    - Yahoo Finance for company-specific news
    - RSS feeds from major financial outlets
    - Web scraping fallback
    """

    def __init__(self):
        self.news_api = None
        if config.api_keys.news_api:
            self.news_api = NewsApiClient(api_key=config.api_keys.news_api)

    def fetch_news_for_ticker(
        self, ticker: str, days_back: int = None
    ) -> List[NewsArticle]:
        """
        Fetch news for a specific stock ticker from multiple sources
        """
        days_back = days_back or config.news.lookback_days
        articles = []

        # 1. Yahoo Finance News (Free, no API key needed)
        articles.extend(self._fetch_yfinance_news(ticker, days_back))

        # 2. NewsAPI (requires API key)
        if self.news_api:
            articles.extend(self._fetch_newsapi_articles(ticker, days_back))

        # 3. RSS Feeds from financial sites
        articles.extend(self._fetch_rss_feeds(ticker))

        logger.info(f"Fetched {len(articles)} articles for {ticker}")
        return articles

    def fetch_market_news(self, keywords: List[str] = None) -> List[NewsArticle]:
        """
        Fetch general market news
        """
        keywords = keywords or ["stock market", "S&P 500", "dow jones", "nasdaq"]
        articles = []

        if self.news_api:
            for keyword in keywords:
                articles.extend(
                    self._fetch_newsapi_articles(
                        keyword, config.news.lookback_days, category="business"
                    )
                )

        # RSS feeds for general market news
        rss_feeds = [
            "https://feeds.reuters.com/reuters/businessNews",
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
        ]

        for feed_url in rss_feeds:
            articles.extend(self._parse_rss_feed(feed_url))

        return articles[:config.news.max_articles]

    def _fetch_yfinance_news(self, ticker: str, days_back: int) -> List[NewsArticle]:
        """Fetch news from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news

            articles = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for item in news:
                pub_date = datetime.fromtimestamp(item.get("providerPublishTime", 0))

                if pub_date < cutoff_date:
                    continue

                articles.append(
                    NewsArticle(
                        title=item.get("title", ""),
                        content=item.get("summary", ""),
                        source="Yahoo Finance",
                        url=item.get("link", ""),
                        published_at=pub_date,
                        ticker=ticker,
                        metadata=item,
                    )
                )

            return articles
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance news for {ticker}: {e}")
            return []

    def _fetch_newsapi_articles(
        self, query: str, days_back: int, category: str = None
    ) -> List[NewsArticle]:
        """Fetch news from NewsAPI"""
        try:
            from_date = (datetime.now() - timedelta(days=days_back)).strftime(
                "%Y-%m-%d"
            )

            params = {
                "q": query,
                "from_param": from_date,
                "language": "en",
                "sort_by": "relevancy",
                "page_size": 100,
            }

            if category:
                params["category"] = category

            response = self.news_api.get_everything(**params)

            articles = []
            for item in response.get("articles", []):
                if not item.get("content"):
                    continue

                articles.append(
                    NewsArticle(
                        title=item["title"],
                        content=item["content"],
                        source=item["source"]["name"],
                        url=item["url"],
                        published_at=datetime.fromisoformat(
                            item["publishedAt"].replace("Z", "+00:00")
                        ),
                        metadata=item,
                    )
                )

            return articles
        except Exception as e:
            logger.error(f"Error fetching NewsAPI articles: {e}")
            return []

    def _fetch_rss_feeds(self, ticker: str) -> List[NewsArticle]:
        """Fetch news from RSS feeds"""
        # Seeking Alpha RSS (example)
        feed_url = f"https://seekingalpha.com/api/sa/combined/{ticker}.xml"
        return self._parse_rss_feed(feed_url, ticker)

    def _parse_rss_feed(
        self, feed_url: str, ticker: Optional[str] = None
    ) -> List[NewsArticle]:
        """Parse RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            articles = []

            for entry in feed.entries[:50]:
                published = entry.get("published_parsed")
                if published:
                    pub_date = datetime(*published[:6])
                else:
                    pub_date = datetime.now()

                content = entry.get("summary", entry.get("description", ""))

                articles.append(
                    NewsArticle(
                        title=entry.get("title", ""),
                        content=content,
                        source=feed.feed.get("title", "RSS Feed"),
                        url=entry.get("link", ""),
                        published_at=pub_date,
                        ticker=ticker,
                    )
                )

            return articles
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {e}")
            return []

    def enrich_with_content(self, article: NewsArticle) -> NewsArticle:
        """
        Scrape full article content if summary is truncated
        Modern approach: Use beautiful soup with smart extraction
        """
        try:
            if len(article.content) > 500:  # Already has good content
                return article

            response = requests.get(article.url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Try to find article content
            article_body = soup.find("article") or soup.find(
                "div", class_=["article-body", "story-body", "entry-content"]
            )

            if article_body:
                paragraphs = article_body.find_all("p")
                full_content = "\n\n".join([p.get_text() for p in paragraphs])
                article.content = full_content[:5000]  # Limit to 5000 chars

            return article
        except Exception as e:
            logger.error(f"Error enriching article content: {e}")
            return article
