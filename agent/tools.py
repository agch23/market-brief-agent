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
    Returns a dict: {ticker: {name, price, change_pct, currency}}
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
