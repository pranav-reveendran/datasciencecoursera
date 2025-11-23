"""
Real-time market data tools for the agents
These tools can be called by LLM agents to get live market data
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from langchain.tools import tool
from ..utils.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@tool
def get_stock_price(ticker: str) -> Dict:
    """
    Get current stock price and key metrics for a given ticker.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

    Returns:
        Dictionary with current price, change, volume, market cap, etc.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker,
            "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
            "previous_close": info.get("previousClose"),
            "open": info.get("open"),
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "volume": info.get("volume"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error fetching stock price for {ticker}: {e}")
        return {"error": str(e)}


@tool
def get_stock_history(ticker: str, period: str = "1mo") -> Dict:
    """
    Get historical stock price data.

    Args:
        ticker: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

    Returns:
        Historical price data with OHLCV
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        return {
            "ticker": ticker,
            "period": period,
            "data": hist.to_dict(orient="index"),
            "summary": {
                "start_price": float(hist['Close'].iloc[0]),
                "end_price": float(hist['Close'].iloc[-1]),
                "change_percent": float(
                    ((hist['Close'].iloc[-1] - hist['Close'].iloc[0])
                     / hist['Close'].iloc[0] * 100)
                ),
                "high": float(hist['High'].max()),
                "low": float(hist['Low'].min()),
                "avg_volume": float(hist['Volume'].mean()),
            }
        }
    except Exception as e:
        logger.error(f"Error fetching history for {ticker}: {e}")
        return {"error": str(e)}


@tool
def get_company_info(ticker: str) -> Dict:
    """
    Get detailed company information and fundamentals.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Company profile, sector, industry, description, executives, etc.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker,
            "name": info.get("longName", info.get("shortName")),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "description": info.get("longBusinessSummary"),
            "website": info.get("website"),
            "employees": info.get("fullTimeEmployees"),
            "city": info.get("city"),
            "state": info.get("state"),
            "country": info.get("country"),
            "market_cap": info.get("marketCap"),
            "revenue": info.get("totalRevenue"),
            "profit_margin": info.get("profitMargins"),
            "beta": info.get("beta"),
            "dividend_yield": info.get("dividendYield"),
        }
    except Exception as e:
        logger.error(f"Error fetching company info for {ticker}: {e}")
        return {"error": str(e)}


@tool
def get_financial_statements(ticker: str) -> Dict:
    """
    Get financial statements (income statement, balance sheet, cash flow).

    Args:
        ticker: Stock ticker symbol

    Returns:
        Financial statements data
    """
    try:
        stock = yf.Ticker(ticker)

        return {
            "ticker": ticker,
            "income_statement": stock.financials.to_dict() if hasattr(stock.financials, 'to_dict') else {},
            "balance_sheet": stock.balance_sheet.to_dict() if hasattr(stock.balance_sheet, 'to_dict') else {},
            "cash_flow": stock.cashflow.to_dict() if hasattr(stock.cashflow, 'to_dict') else {},
            "quarterly_financials": stock.quarterly_financials.to_dict() if hasattr(stock.quarterly_financials, 'to_dict') else {},
        }
    except Exception as e:
        logger.error(f"Error fetching financials for {ticker}: {e}")
        return {"error": str(e)}


@tool
def get_analyst_recommendations(ticker: str) -> Dict:
    """
    Get analyst recommendations and price targets.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Analyst ratings, price targets, and recommendations
    """
    try:
        stock = yf.Ticker(ticker)

        recommendations = stock.recommendations
        if recommendations is not None and not recommendations.empty:
            recent = recommendations.tail(10).to_dict(orient="records")
        else:
            recent = []

        info = stock.info

        return {
            "ticker": ticker,
            "target_high_price": info.get("targetHighPrice"),
            "target_low_price": info.get("targetLowPrice"),
            "target_mean_price": info.get("targetMeanPrice"),
            "target_median_price": info.get("targetMedianPrice"),
            "recommendation": info.get("recommendationKey"),
            "number_of_analysts": info.get("numberOfAnalystOpinions"),
            "recent_recommendations": recent,
        }
    except Exception as e:
        logger.error(f"Error fetching recommendations for {ticker}: {e}")
        return {"error": str(e)}


@tool
def compare_stocks(tickers: List[str]) -> Dict:
    """
    Compare multiple stocks side by side.

    Args:
        tickers: List of stock ticker symbols

    Returns:
        Comparative metrics across stocks
    """
    try:
        comparison = {}

        for ticker in tickers:
            stock = yf.Ticker(ticker)
            info = stock.info

            comparison[ticker] = {
                "price": info.get("currentPrice", info.get("regularMarketPrice")),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield"),
                "profit_margin": info.get("profitMargins"),
                "beta": info.get("beta"),
                "52w_change": info.get("52WeekChange"),
            }

        return {
            "comparison": comparison,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error comparing stocks: {e}")
        return {"error": str(e)}


@tool
def search_ticker(company_name: str) -> Dict:
    """
    Search for ticker symbol by company name.

    Args:
        company_name: Company name to search for

    Returns:
        Ticker symbol and basic info
    """
    try:
        # Use yfinance search (basic implementation)
        # In production, you might want to use a dedicated API
        ticker = yf.Ticker(company_name.upper().replace(" ", ""))
        info = ticker.info

        if info.get("symbol"):
            return {
                "ticker": info.get("symbol"),
                "name": info.get("longName", info.get("shortName")),
                "exchange": info.get("exchange"),
                "type": info.get("quoteType"),
            }
        else:
            return {"error": "Ticker not found"}

    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}


# Collection of all tools for agent use
MARKET_TOOLS = [
    get_stock_price,
    get_stock_history,
    get_company_info,
    get_financial_statements,
    get_analyst_recommendations,
    compare_stocks,
    search_ticker,
]
