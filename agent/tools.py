"""
Tools the agent uses to gather data.
Each function does ONE thing and returns clean data.
"""

import os
import yfinance as yf
import requests
from datetime import datetime, timedelta
from config import ALL_INSTRUMENTS, MACRO_NEWS_TOPICS


def get_price_snapshot():
    """
    Fetches latest price + 1-day change for every instrument in the watchlist.
    Returns a dict: {ticker: {name, price, change_pct}}
    """
    snapshot = {}
    for ticker, name in ALL_INSTRUMENTS.items():
        try:
            data = yf.Ticker(ticker).history(period="2d")
            if len(data) >= 2:
                prev_close = data["Close"].iloc[-2]
                last_price = data["Close"].iloc[-1]
                change_pct = ((last_price - prev_close) / prev_close) * 100
                snapshot[ticker] = {
                    "name": name,
                    "price": round(float(last_price), 2),
                    "change_pct": round(float(change_pct), 2),
                }
            else:
                snapshot[ticker] = {"name": name, "error": "insufficient data"}
        except Exception as e:
            snapshot[ticker] = {"name": name, "error": str(e)}
    return snapshot


def get_news_for_ticker(ticker_name, max_articles=3):
    """
    Fetches recent news headlines for a specific company or topic.
    Returns a list of {title, source, url, published}.
    """
    api_key = os.environ.get("NEWSAPI_KEY")
    if not api_key:
        return [{"error": "NEWSAPI_KEY not set"}]

    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": ticker_name,
        "from": yesterday,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": max_articles,
        "apiKey": api_key,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        return [
            {
                "title": a.get("title"),
                "source": a.get("source", {}).get("name"),
                "url": a.get("url"),
                "published": a.get("publishedAt"),
            }
            for a in articles
        ]
    except Exception as e:
        return [{"error": str(e)}]


def get_macro_news():
    """
    Fetches headlines on macro themes (Fed, ECB, geopolitics, oil).
    Returns a flat list of articles across all topics.
    """
    all_articles = []
    for topic in MACRO_NEWS_TOPICS:
        articles = get_news_for_ticker(topic, max_articles=2)
        for a in articles:
            if "error" not in a:
                a["topic"] = topic
                all_articles.append(a)
    return all_articles


# ============================================================
# Tool definitions for Claude — these tell the agent what's available
# ============================================================

TOOL_DEFINITIONS = [
    {
        "name": "get_price_snapshot",
        "description": "Returns current price and 1-day percent change for all 26 watchlist instruments. Call this FIRST every brief.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_news_for_ticker",
        "description": "Fetches recent news for a specific company or ticker. Use for stocks showing unusual price moves.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker_name": {
                    "type": "string",
                    "description": "Company name or ticker (e.g., 'Nvidia', 'ASML', 'Apple').",
                },
                "max_articles": {
                    "type": "integer",
                    "description": "Number of articles (default 3).",
                },
            },
            "required": ["ticker_name"],
        },
    },
    {
        "name": "get_macro_news",
        "description": "Fetches headlines on macro themes (Fed, ECB, oil, geopolitics). Call once per brief for context.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]


def execute_tool(tool_name, tool_input):
    """Dispatcher — runs the right function when Claude requests a tool."""
    if tool_name == "get_price_snapshot":
        return get_price_snapshot()
    elif tool_name == "get_news_for_ticker":
        return get_news_for_ticker(
            tool_input.get("ticker_name"),
            tool_input.get("max_articles", 3),
        )
    elif tool_name == "get_macro_news":
        return get_macro_news()
    else:
        return {"error": f"Unknown tool: {tool_name}"}
