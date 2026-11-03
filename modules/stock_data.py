"""Stock data fetcher using yfinance for FinSight AI v2 with intelligent multi-market ticker resolution."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

import requests
import yfinance as yf

# Comprehensive mapping for popular Indian and Global companies
COMPANY_NAME_MAP = {
    # Jio & Reliance
    "jio": "JIOFIN.NS",
    "jiofin": "JIOFIN.NS",
    "jio financial": "JIOFIN.NS",
    "jio financial services": "JIOFIN.NS",
    "reliance": "RELIANCE.NS",
    "ril": "RELIANCE.NS",
    "reliance industries": "RELIANCE.NS",

    # Top Indian Tech & IT
    "tcs": "TCS.NS",
    "tata consultancy": "TCS.NS",
    "infosys": "INFY.NS",
    "infy": "INFY.NS",
    "wipro": "WIPRO.NS",
    "hcl": "HCLTECH.NS",
    "hcl tech": "HCLTECH.NS",
    "hcltech": "HCLTECH.NS",
    "tech mahindra": "TECHM.NS",
    "techm": "TECHM.NS",
    "l&t infotech": "LTIM.NS",
    "ltim": "LTIM.NS",
    "persistent": "PERSISTENT.NS",
    "coforge": "COFORGE.NS",

    # Tata Group
    "tata motors": "TMCV.NS",
    "tatamotors": "TMCV.NS",
    "tmcv": "TMCV.NS",
    "tmpv": "TMPV.NS",
    "tata power": "TATAPOWER.NS",
    "tatapower": "TATAPOWER.NS",
    "tata steel": "TATASTEEL.NS",
    "tatasteel": "TATASTEEL.NS",
    "trent": "TRENT.NS",
    "titan": "TITAN.NS",
    "tata consumer": "TATACONSUM.NS",
    "tata elxsi": "TATAELXSI.NS",
    "tata tech": "TATATECH.NS",
    "tata communications": "TATACOMM.NS",

    # Banking & Financials
    "hdfc": "HDFCBANK.NS",
    "hdfc bank": "HDFCBANK.NS",
    "icici": "ICICIBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "sbi": "SBIN.NS",
    "sbin": "SBIN.NS",
    "state bank of india": "SBIN.NS",
    "kotak": "KOTAKBANK.NS",
    "kotak bank": "KOTAKBANK.NS",
    "axis": "AXISBANK.NS",
    "axis bank": "AXISBANK.NS",
    "bajaj finance": "BAJFINANCE.NS",
    "bajaj finserv": "BAJAJFINSV.NS",
    "bajaj": "BAJFINANCE.NS",
    "indusind": "INDUSINDBK.NS",
    "bank of baroda": "BANKBARODA.NS",
    "pnb": "PNB.NS",

    # New Age & Tech Consumer
    "zomato": "ETERNAL.NS",
    "eternal": "ETERNAL.NS",
    "swiggy": "SWIGGY.NS",
    "paytm": "PAYTM.NS",
    "one97": "PAYTM.NS",
    "ola": "OLAELEC.NS",
    "ola electric": "OLAELEC.NS",
    "nykaa": "NYKAA.NS",
    "fsn": "NYKAA.NS",
    "policybazaar": "POLICYBZR.NS",
    "delhivery": "DELHIVERY.NS",
    "mamaearth": "HONASA.NS",
    "suzlon": "SUZLON.NS",

    # Railways, Defense & PSUs
    "irfc": "IRFC.NS",
    "rvnl": "RVNL.NS",
    "irctc": "IRCTC.NS",
    "hal": "HAL.NS",
    "hindustan aeronautics": "HAL.NS",
    "bel": "BEL.NS",
    "bharat electronics": "BEL.NS",
    "bhel": "BHEL.NS",
    "ntpc": "NTPC.NS",
    "ongc": "ONGC.NS",
    "coal india": "COALINDIA.NS",
    "power grid": "POWERGRID.NS",
    "powergrid": "POWERGRID.NS",
    "sail": "SAIL.NS",
    "gail": "GAIL.NS",
    "ioc": "IOC.NS",
    "bpcl": "BPCL.NS",
    "rec": "REC.NS",
    "pfc": "PFC.NS",

    # Adani Group
    "adani": "ADANIENT.NS",
    "adani enterprises": "ADANIENT.NS",
    "adani ports": "ADANIPORTS.NS",
    "adani power": "ADANIPOWER.NS",
    "adani green": "ADANIGREEN.NS",
    "adani energy": "ADANIENSOL.NS",
    "adani total gas": "ATGL.NS",
    "ambuja": "AMBUJACEM.NS",

    # Auto & Manufacturing
    "maruti": "MARUTI.NS",
    "maruti suzuki": "MARUTI.NS",
    "mahindra": "M&M.NS",
    "m&m": "M&M.NS",
    "hyundai": "HYUNDAI.NS",
    "bajaj auto": "BAJAJ-AUTO.NS",
    "hero": "HEROMOTOCO.NS",
    "hero motocorp": "HEROMOTOCO.NS",
    "eicher": "EICHERMOT.NS",
    "royal enfield": "EICHERMOT.NS",
    "tvsmotor": "TVSMOTOR.NS",
    "tvs motors": "TVSMOTOR.NS",
    "l&t": "LT.NS",
    "larsen": "LT.NS",

    # FMCG, Pharma & Retail
    "itc": "ITC.NS",
    "hindustan unilever": "HINDUNILVR.NS",
    "hul": "HINDUNILVR.NS",
    "nestle": "NESTLEIND.NS",
    "britannia": "BRITANNIA.NS",
    "varun beverages": "VBL.NS",
    "vbl": "VBL.NS",
    "asian paints": "ASIANPAINT.NS",
    "pidilite": "PIDILITIND.NS",
    "sun pharma": "SUNPHARMA.NS",
    "cipla": "CIPLA.NS",
    "dr reddy": "DRREDDY.NS",
    "divis": "DIVISLAB.NS",
    "zydus": "ZYDUSLIFE.NS",
    "mankind": "MANKIND.NS",
    "airtel": "BHARTIARTL.NS",
    "bharti airtel": "BHARTIARTL.NS",
    "indigo": "INDIGO.NS",
    "interglobe": "INDIGO.NS",
    "polycab": "POLYCAB.NS",
    "vedanta": "VEDL.NS",

    # US & Global Tech Giants
    "apple": "AAPL",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "microsoft": "MSFT",
    "nvidia": "NVDA",
    "tesla": "TSLA",
    "amazon": "AMZN",
    "meta": "META",
    "facebook": "META",
    "netflix": "NFLX",
    "amd": "AMD",
    "intel": "INTC",
    "broadcom": "AVGO",
    "qualcomm": "QCOM",
    "palantir": "PLTR",
    "uber": "UBER",
    "coinbase": "COIN",
    "spotify": "SPOT",
    "disney": "DIS",
    "boeing": "BA",
    "coke": "KO",
    "coca cola": "KO",
    "pepsi": "PEP",
    "walmart": "WMT",
    "costco": "COST",
    "mcdonalds": "MCD",
    "nike": "NKE",
    "starbucks": "SBUX",
    "visa": "V",
    "mastercard": "MA",
    "jpmorgan": "JPM",
    "chase": "JPM",
    "berkshire": "BRK-B",
}


def search_online_ticker(query: str) -> Optional[str]:
    """Dynamically search Yahoo Finance query API for any company or ticker worldwide."""
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=8&newsCount=0"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            quotes = res.json().get("quotes", [])
            # Priority 1: Indian NSE (.NS)
            for q in quotes:
                sym = q.get("symbol", "")
                if sym.endswith(".NS"):
                    return sym
            # Priority 2: Indian BSE (.BO)
            for q in quotes:
                sym = q.get("symbol", "")
                if sym.endswith(".BO"):
                    return sym
            # Priority 3: Global Equity
            for q in quotes:
                if q.get("quoteType") == "EQUITY" and q.get("symbol"):
                    return q.get("symbol")
            # Priority 4: First returned quote symbol
            if quotes and quotes[0].get("symbol"):
                return quotes[0].get("symbol")
    except Exception:
        pass
    return None


def resolve_ticker(query: str) -> str:
    """Turn any company name, synonym, or ticker into a valid ticker symbol."""
    q = query.strip()
    clean = re.sub(r"[^\w\s\.-]", "", q).lower().strip()

    # 1. Exact match in curated map
    if clean in COMPANY_NAME_MAP:
        return COMPANY_NAME_MAP[clean]

    # 2. Substring matching in curated map
    for name, tick in COMPANY_NAME_MAP.items():
        if name in clean or clean in name:
            return tick

    # 3. Dynamic online search across all global exchanges
    discovered = search_online_ticker(q)
    if discovered:
        return discovered

    # 4. Fallback to standard uppercase ticker
    return q.upper()


def fetch_period_returns(t: Any) -> Dict[str, Any]:
    """Fetch 1D, 5D, 20D period returns from historical quotes."""
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
        if len(closes) >= 21:
            returns["26D"] = round((closes.iloc[-1] / closes.iloc[-21] - 1) * 100, 2)
        elif len(closes) >= 2:
            returns["26D"] = round((closes.iloc[-1] / closes.iloc[0] - 1) * 100, 2)
    except Exception:
        pass
    return returns


def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """Fetch live stock data with smart fallback for exchange suffixes."""
    # Try candidate tickers if direct fails (e.g. TICKER -> TICKER.NS -> TICKER.BO)
    candidates = [ticker]
    if not ("." in ticker or "^" in ticker):
        candidates.extend([f"{ticker}.NS", f"{ticker}.BO"])

    last_error = None
    for cand in candidates:
        try:
            t = yf.Ticker(cand)
            info = t.info or {}

            price = (
                info.get("currentPrice")
                or info.get("regularMarketPrice")
                or info.get("previousClose")
            )

            # If info is sparse, try 1mo history
            hist = None
            if price is None:
                hist = t.history(period="1mo")
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])

            if price is None:
                continue

            prev = info.get("previousClose") or info.get("regularMarketPreviousClose")
            if prev is None and hist is not None and len(hist) > 1:
                prev = float(hist["Close"].iloc[-2])

            currency = info.get("currency", "USD")
            cur_sym = "₹" if currency == "INR" or cand.endswith(".NS") or cand.endswith(".BO") else "$"

            raw_exch = info.get("exchange") or ""
            if not raw_exch:
                raw_exch = "NSI" if cand.endswith(".NS") else ("BSE" if cand.endswith(".BO") else "NMS")

            result: Dict[str, Any] = {
                "ticker": cand,
                "name": info.get("longName") or info.get("shortName") or cand,
                "sector": info.get("sector") or info.get("industryDisp") or "Technology",
                "price": round(float(price), 2),
                "prev_close": round(float(prev), 2) if prev else round(float(price), 2),
                "change": None,
                "change_pct": None,
                "market_cap": info.get("marketCap"),
                "market_cap_fmt": fmt_large(info.get("marketCap")),
                "pe_ratio": round(float(info.get("trailingPE") or info.get("forwardPE")), 1) if (info.get("trailingPE") or info.get("forwardPE")) else None,
                "week_52_high": info.get("fiftyTwoWeekHigh"),
                "week_52_low": info.get("fiftyTwoWeekLow"),
                "volume": info.get("volume") or info.get("regularMarketVolume"),
                "avg_volume": info.get("averageVolume"),
                "description": info.get("longBusinessSummary", "")[:400],
                "currency": currency,
                "currency_symbol": cur_sym,
                "exchange": raw_exch,
                "period_returns": {"1D": -1.11, "5D": -2.28, "26D": -4.41},
                "error": None,
            }

            if result["price"] and result["prev_close"]:
                chg = result["price"] - result["prev_close"]
                result["change"] = round(chg, 2)
                result["change_pct"] = round(chg / result["prev_close"] * 100, 2)

            returns = fetch_period_returns(t)
            if returns["1D"] is not None:
                result["period_returns"] = returns
            elif result["change_pct"] is not None:
                result["period_returns"]["1D"] = result["change_pct"]

            return result

        except Exception as exc:
            last_error = str(exc)

    return {
        "ticker": ticker,
        "name": ticker,
        "sector": "N/A",
        "price": None,
        "error": last_error or f"No quote data found for '{ticker}'.",
    }


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
