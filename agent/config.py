"""
Configuration for the Market Brief Agent.
Edit this file to customize the watchlist or behavior.
"""

# ============================================================
# WATCHLIST — 26 instruments across global markets
# ============================================================

US_STOCKS = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "META": "Meta Platforms",
    "JPM": "JPMorgan Chase",
    "XOM": "ExxonMobil",
}

EUROPE_STOCKS = {
    "ASML.AS": "ASML",
    "MC.PA": "LVMH",
    "NOVO-B.CO": "Novo Nordisk",
    "SAP.DE": "SAP",
    "SHEL.L": "Shell",
}

ASIA_STOCKS = {
    "TSM": "TSMC (US ADR)",
    "005930.KS": "Samsung Electronics",
    "7203.T": "Toyota",
    "BABA": "Alibaba",
}

ETFS = {
    "SPY": "S&P 500 ETF",
    "EZU": "Eurozone ETF",
    "EWJ": "Japan ETF",
    "ACWI": "Global ETF",
}

MACRO_SIGNALS = {
    "^VIX": "Volatility Index",
    "DX-Y.NYB": "US Dollar Index",
    "^TNX": "US 10-Year Yield",
    "BZ=F": "Brent Crude",
    "GC=F": "Gold",
}

# Combined dictionary for easy iteration
ALL_INSTRUMENTS = {
    **US_STOCKS,
    **EUROPE_STOCKS,
    **ASIA_STOCKS,
    **ETFS,
    **MACRO_SIGNALS,
}

# ============================================================
# AGENT BEHAVIOR
# ============================================================

CLAUDE_MODEL = "claude-opus-4-7"  # Top-tier reasoning for analysis
MAX_TOOL_ITERATIONS = 8           # Safety cap on agent loop
BRIEF_TIMEZONE = "Europe/Madrid"  # CET — adjust if you relocate

# News search keywords for macro context
MACRO_NEWS_TOPICS = [
    "Federal Reserve",
    "ECB monetary policy",
    "oil prices Hormuz",
    "global markets",
]
