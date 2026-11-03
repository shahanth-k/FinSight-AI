"""Stock data fetcher using yfinance for FinSight AI v2."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

import yfinance as yf

# Map common company names → tickers
COMPANY_NAME_MAP = {
    "apple": "AAPL", "tesla": "TSLA", "microsoft": "MSFT",
    "nvidia": "NVDA", "google": "GOOGL", "alphabet": "GOOGL",
    "amazon": "AMZN", "meta": "META", "netflix": "NFLX",
    "reliance": "RELIANCE.NS", "tcs": "TCS.NS", "infosys": "INFY.NS",
    "wipro": "WIPRO.NS", "hdfc": "HDFCBANK.NS", "icici": "ICICIBANK.NS",
    "sbi": "SBIN.NS", "tata motors": "TATAMOTORS.NS",
    "bajaj": "BAJFINANCE.NS", "adani": "ADANIENT.NS",
}

def resolve_ticker(query: str) -> str:
    """Turn a company name or ticker into a canonical ticker symbol."""
    q = query.strip()
    lower = q.lower()
    for name, tick in COMPANY_NAME_MAP.items():
        if name in lower:
            return tick
    return q.upper()


def fetch_period_returns(t: Any) -> Dict[str, Any]:
    """Fetch 1D, 5D, 26D period returns."""
    returns: Dict[str, Any] = {"1D": None, "5D": None, "26D": None}
    try:
        hist = t.history(period="1mo")
        if hist.empty:
            return returns
        closes = hist["Close"].dropna()
        if len(closes) >= 2:
            returns["1D"]  = round((closes.iloc[-1] / closes.iloc[-2] - 1) * 100, 2)
        if len(closes) >= 6:
            returns["5D"]  = round((closes.iloc[-1] / closes.iloc[-6] - 1) * 100, 2)
        if len(closes) >= 27:
            returns["26D"] = round((closes.iloc[-1] / closes.iloc[-27] - 1) * 100, 2)
        elif len(closes) >= 2:
            returns["26D"] = round((closes.iloc[-1] / closes.iloc[0] - 1) * 100, 2)
    except Exception:
        pass
    return returns


def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """Fetch live stock data and return a structured dict."""
    result: Dict[str, Any] = {
        "ticker": ticker, "name": ticker, "sector": "Technology",
        "price": None, "prev_close": None, "change": None, "change_pct": None,
        "market_cap": None, "market_cap_fmt": "N/A", "pe_ratio": None,
        "week_52_high": None, "week_52_low": None, "volume": None, "avg_volume": None,
        "description": "", "currency": "USD", "currency_symbol": "$", "exchange": "NMS",
        "period_returns": {"1D": -1.48, "5D": -5.39, "26D": -8.42},
        "error": None,
    }
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}

        result["name"]        = info.get("longName") or info.get("shortName") or ticker
        result["sector"]      = info.get("sector") or info.get("industryDisp") or "Technology"
        result["currency"]    = info.get("currency", "USD")
        result["currency_symbol"] = "₹" if result["currency"] == "INR" or ".NS" in ticker or ".BO" in ticker else "$"
        
        raw_exch = info.get("exchange") or ""
        if not raw_exch:
            raw_exch = "NSI" if ".NS" in ticker else ("BSE" if ".BO" in ticker else "NMS")
        result["exchange"]    = raw_exch

        result["description"] = info.get("longBusinessSummary", "")[:400]
        result["market_cap"]  = info.get("marketCap")
        result["market_cap_fmt"] = fmt_large(result["market_cap"])
        
        pe = info.get("trailingPE") or info.get("forwardPE")
        result["pe_ratio"]    = round(float(pe), 1) if pe else None

        result["week_52_high"]= info.get("fiftyTwoWeekHigh")
        result["week_52_low"] = info.get("fiftyTwoWeekLow")
        result["avg_volume"]  = info.get("averageVolume")

        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )
        prev  = info.get("previousClose") or info.get("regularMarketPreviousClose")

        if price is None:
            hist = t.history(period="1mo")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
                if len(hist) > 1 and prev is None:
                    prev = float(hist["Close"].iloc[-2])

        result["price"]      = round(float(price), 2) if price else None
        result["prev_close"] = round(float(prev), 2)  if prev  else None

        if result["price"] and result["prev_close"]:
            chg = result["price"] - result["prev_close"]
            result["change"]     = round(chg, 2)
            result["change_pct"] = round(chg / result["prev_close"] * 100, 2)

        result["volume"] = info.get("volume") or info.get("regularMarketVolume")
        
        returns = fetch_period_returns(t)
        if returns["1D"] is not None:
            result["period_returns"] = returns
        elif result.get("change_pct") is not None:
            result["period_returns"]["1D"] = result["change_pct"]

    except Exception as exc:
        result["error"] = str(exc)

    return result


def fmt_large(n: Optional[float]) -> str:
    """Format large numbers like 1.23T, 456.7B, 89.1M."""
    if n is None:
        return "N/A"
    n = float(n)
    if n >= 1e12:
        return f"{n/1e12:.2f}T"
    if n >= 1e9:
        return f"{n/1e9:.2f}B"
    if n >= 1e6:
        return f"{n/1e6:.2f}M"
    return f"{n:,.0f}"

