"""
FinSight AI - Technical Analysis Engine
Deterministic, transparent calculations for all market indicators.
No AI guessing here — pure math and statistics.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class TechnicalAnalysisEngine:

    TICKER_MAP = {
        # US Tech
        "APPLE": "AAPL", "MICROSOFT": "MSFT", "GOOGLE": "GOOGL",
        "ALPHABET": "GOOGL", "AMAZON": "AMZN", "TESLA": "TSLA",
        "META": "META", "FACEBOOK": "META", "NETFLIX": "NFLX",
        "NVIDIA": "NVDA", "AMD": "AMD", "INTEL": "INTC",
        "SALESFORCE": "CRM", "ADOBE": "ADBE", "ORACLE": "ORCL",
        "IBM": "IBM", "QUALCOMM": "QCOM", "TEXAS INSTRUMENTS": "TXN",
        "BROADCOM": "AVGO", "MICRON": "MU", "PAYPAL": "PYPL",
        "SPOTIFY": "SPOT", "UBER": "UBER", "LYFT": "LYFT",
        "AIRBNB": "ABNB", "COINBASE": "COIN", "PALANTIR": "PLTR",
        # US Finance
        "JPMORGAN": "JPM", "JP MORGAN": "JPM", "GOLDMAN SACHS": "GS",
        "BANK OF AMERICA": "BAC", "WELLS FARGO": "WFC",
        "MORGAN STANLEY": "MS", "VISA": "V", "MASTERCARD": "MA",
        "AMERICAN EXPRESS": "AXP", "BERKSHIRE": "BRK-B",
        # US Consumer
        "WALMART": "WMT", "TARGET": "TGT", "COSTCO": "COST",
        "MCDONALDS": "MCD", "STARBUCKS": "SBUX", "COCA COLA": "KO",
        "PEPSI": "PEP", "JOHNSON AND JOHNSON": "JNJ", "PFIZER": "PFE",
        "DISNEY": "DIS",
        # Indian Stocks (NSE)
        "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS",
        "INFOSYS": "INFY.NS", "WIPRO": "WIPRO.NS",
        "HDFC BANK": "HDFCBANK.NS", "HDFC": "HDFC.NS",
        "ICICI BANK": "ICICIBANK.NS", "ICICI": "ICICIBANK.NS",
        "AXIS BANK": "AXISBANK.NS", "SBI": "SBIN.NS",
        "BAJAJ FINANCE": "BAJFINANCE.NS", "HINDUSTAN UNILEVER": "HINDUNILVR.NS",
        "HUL": "HINDUNILVR.NS", "ITC": "ITC.NS", "ADANI": "ADANIENT.NS",
        "TATA MOTORS": "TATAMOTORS.NS", "TATA STEEL": "TATASTEEL.NS",
        "MARUTI": "MARUTI.NS", "ASIAN PAINTS": "ASIANPAINT.NS",
        "KOTAK": "KOTAKBANK.NS", "NIFTY": "^NSEI",
    }

    def analyze(self, query: str) -> dict:
        ticker = self._resolve_ticker(query)
        if not ticker:
            return {"error": f"Could not find a valid stock for: '{query}'. Please try the ticker symbol directly (e.g. AAPL, TSLA)."}

        try:
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=400)  # ~14 months for SMA200
            hist = stock.history(start=start_date, end=end_date, auto_adjust=True)

            if hist.empty or len(hist) < 20:
                return {"error": f"Insufficient market data for '{ticker}'. The stock may be delisted or the ticker is incorrect."}

            info = self._safe_info(stock)
            company_name = info.get("longName", info.get("shortName", ticker))
            df = hist.copy()

            # ── Calculate all indicators ──────────────────────────────────
            df = self._add_moving_averages(df)
            df = self._add_rsi(df)
            df = self._add_macd(df)
            df = self._add_bollinger_bands(df)
            df = self._add_atr(df)
            df = self._add_volume_analysis(df)
            df = self._add_momentum(df)

            latest = df.iloc[-1]
            current_price = float(latest["Close"])

            support, resistance = self._calc_support_resistance(df)
            trend = self._determine_trend(df, current_price)
            signals = self._generate_signals(df, latest, current_price, support, resistance)
            volatility_annual = float(df["Close"].pct_change().dropna().std() * np.sqrt(252) * 100)
            chart_data = self._prepare_chart_data(df)
            data_quality = self._assess_data_quality(df)

            return {
                "ticker": ticker,
                "company_name": company_name,
                "exchange": info.get("exchange", ""),
                "currency": info.get("currency", "USD"),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE"),
                "week_52_high": info.get("fiftyTwoWeekHigh"),
                "week_52_low": info.get("fiftyTwoWeekLow"),
                "avg_volume": info.get("averageVolume", 0),
                "current_price": round(current_price, 2),
                "price_change_1d": self._safe_pct_change(df, 1),
                "price_change_5d": self._safe_pct_change(df, 5),
                "price_change_20d": self._safe_pct_change(df, 20),
                "sma20": self._round_safe(latest.get("SMA20")),
                "sma50": self._round_safe(latest.get("SMA50")),
                "sma200": self._round_safe(latest.get("SMA200")),
                "ema12": self._round_safe(latest.get("EMA12")),
                "ema26": self._round_safe(latest.get("EMA26")),
                "rsi": self._round_safe(latest.get("RSI"), 1),
                "macd": self._round_safe(latest.get("MACD"), 4),
                "macd_signal": self._round_safe(latest.get("MACD_Signal"), 4),
                "macd_histogram": self._round_safe(latest.get("MACD_Histogram"), 4),
                "bb_upper": self._round_safe(latest.get("BB_Upper")),
                "bb_lower": self._round_safe(latest.get("BB_Lower")),
                "bb_middle": self._round_safe(latest.get("BB_Middle")),
                "bb_width_pct": self._round_safe(
                    ((latest.get("BB_Upper", 0) - latest.get("BB_Lower", 0)) / max(latest.get("BB_Middle", 1), 0.01)) * 100, 2
                ),
                "atr": self._round_safe(latest.get("ATR")),
                "atr_pct": self._round_safe((latest.get("ATR", 0) / current_price) * 100, 2),
                "volatility_annualized": round(volatility_annual, 2),
                "momentum_5d": self._round_safe(latest.get("MOM5"), 2),
                "momentum_10d": self._round_safe(latest.get("MOM10"), 2),
                "volume": int(latest.get("Volume", 0)),
                "volume_ma20": self._round_safe(latest.get("VOL_MA20"), 0),
                "volume_ratio": self._round_safe(
                    latest.get("Volume", 0) / max(latest.get("VOL_MA20", 1), 1), 2
                ),
                "support": round(support, 2),
                "resistance": round(resistance, 2),
                "trend": trend,
                "signals": signals,
                "chart_data": chart_data,
                "data_quality": data_quality,
            }

        except Exception as e:
            return {"error": f"Analysis failed for '{query}': {str(e)}"}

    # ── Indicator Calculations ─────────────────────────────────────────────

    def _add_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["SMA200"] = df["Close"].rolling(200).mean()
        df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
        df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
        return df

    def _add_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        delta = df["Close"].diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        df["RSI"] = 100 - (100 / (1 + rs))
        return df

    def _add_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        df["MACD"] = df["EMA12"] - df["EMA26"]
        df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["MACD_Histogram"] = df["MACD"] - df["MACD_Signal"]
        return df

    def _add_bollinger_bands(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        df["BB_Middle"] = df["Close"].rolling(period).mean()
        std = df["Close"].rolling(period).std()
        df["BB_Upper"] = df["BB_Middle"] + 2 * std
        df["BB_Lower"] = df["BB_Middle"] - 2 * std
        return df

    def _add_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        prev_close = df["Close"].shift(1)
        tr = pd.concat([
            df["High"] - df["Low"],
            (df["High"] - prev_close).abs(),
            (df["Low"] - prev_close).abs(),
        ], axis=1).max(axis=1)
        df["ATR"] = tr.rolling(period).mean()
        return df

    def _add_volume_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        df["VOL_MA20"] = df["Volume"].rolling(20).mean()
        return df

    def _add_momentum(self, df: pd.DataFrame) -> pd.DataFrame:
        df["MOM5"] = df["Close"].pct_change(5) * 100
        df["MOM10"] = df["Close"].pct_change(10) * 100
        return df

    # ── Signal Generation ──────────────────────────────────────────────────

    def _generate_signals(self, df, latest, price, support, resistance) -> list:
        signals = []

        # RSI
        rsi = self._get_val(latest, "RSI")
        if rsi is not None:
            if rsi >= 70:
                signals.append({"indicator": "RSI", "value": f"{rsi:.1f}", "signal": "Bearish",
                                 "description": "Overbought — selling pressure likely", "score": -1.0, "weight": 1.2})
            elif rsi <= 30:
                signals.append({"indicator": "RSI", "value": f"{rsi:.1f}", "signal": "Bullish",
                                 "description": "Oversold — potential reversal", "score": 1.0, "weight": 1.2})
            elif rsi >= 55:
                signals.append({"indicator": "RSI", "value": f"{rsi:.1f}", "signal": "Bullish",
                                 "description": "Bullish momentum zone", "score": 0.6, "weight": 1.2})
            elif rsi <= 45:
                signals.append({"indicator": "RSI", "value": f"{rsi:.1f}", "signal": "Bearish",
                                 "description": "Bearish momentum zone", "score": -0.6, "weight": 1.2})
            else:
                signals.append({"indicator": "RSI", "value": f"{rsi:.1f}", "signal": "Neutral",
                                 "description": "Neutral momentum range", "score": 0.0, "weight": 1.2})

        # MACD
        macd = self._get_val(latest, "MACD")
        macd_sig = self._get_val(latest, "MACD_Signal")
        macd_hist = self._get_val(latest, "MACD_Histogram")
        if macd is not None and macd_sig is not None:
            if macd > macd_sig:
                score = 1.0 if (macd_hist or 0) > 0 else 0.5
                signals.append({"indicator": "MACD", "value": f"{macd:.4f}", "signal": "Bullish",
                                 "description": "MACD above signal — bullish crossover", "score": score, "weight": 1.3})
            else:
                score = -1.0 if (macd_hist or 0) < 0 else -0.5
                signals.append({"indicator": "MACD", "value": f"{macd:.4f}", "signal": "Bearish",
                                 "description": "MACD below signal — bearish crossover", "score": score, "weight": 1.3})

        # SMA 20
        sma20 = self._get_val(latest, "SMA20")
        if sma20 is not None:
            if price > sma20:
                signals.append({"indicator": "SMA 20", "value": f"{sma20:.2f}", "signal": "Bullish",
                                 "description": "Price above 20-day moving average", "score": 0.7, "weight": 1.0})
            else:
                signals.append({"indicator": "SMA 20", "value": f"{sma20:.2f}", "signal": "Bearish",
                                 "description": "Price below 20-day moving average", "score": -0.7, "weight": 1.0})

        # SMA 50
        sma50 = self._get_val(latest, "SMA50")
        if sma50 is not None:
            if price > sma50:
                signals.append({"indicator": "SMA 50", "value": f"{sma50:.2f}", "signal": "Bullish",
                                 "description": "Price above 50-day moving average", "score": 0.8, "weight": 1.2})
            else:
                signals.append({"indicator": "SMA 50", "value": f"{sma50:.2f}", "signal": "Bearish",
                                 "description": "Price below 50-day moving average", "score": -0.8, "weight": 1.2})

        # SMA 200
        sma200 = self._get_val(latest, "SMA200")
        if sma200 is not None:
            if price > sma200:
                signals.append({"indicator": "SMA 200", "value": f"{sma200:.2f}", "signal": "Bullish",
                                 "description": "Price above 200-day MA — long-term bullish", "score": 1.0, "weight": 1.5})
            else:
                signals.append({"indicator": "SMA 200", "value": f"{sma200:.2f}", "signal": "Bearish",
                                 "description": "Price below 200-day MA — long-term bearish", "score": -1.0, "weight": 1.5})

        # Bollinger Bands
        bb_u = self._get_val(latest, "BB_Upper")
        bb_l = self._get_val(latest, "BB_Lower")
        if bb_u is not None and bb_l is not None and (bb_u - bb_l) > 0:
            bb_pct = (price - bb_l) / (bb_u - bb_l)
            if bb_pct > 0.85:
                signals.append({"indicator": "Bollinger Bands", "value": f"{bb_pct*100:.0f}%B",
                                 "signal": "Bearish", "description": "Near upper band — overextended", "score": -0.5, "weight": 0.7})
            elif bb_pct < 0.15:
                signals.append({"indicator": "Bollinger Bands", "value": f"{bb_pct*100:.0f}%B",
                                 "signal": "Bullish", "description": "Near lower band — oversold bounce zone", "score": 0.5, "weight": 0.7})
            else:
                signals.append({"indicator": "Bollinger Bands", "value": f"{bb_pct*100:.0f}%B",
                                 "signal": "Neutral", "description": "Price within normal BB range", "score": 0.0, "weight": 0.7})

        # Volume
        vol = float(latest.get("Volume", 0))
        vol_ma = self._get_val(latest, "VOL_MA20")
        if vol_ma and vol_ma > 0:
            ratio = vol / vol_ma
            pct_chg = self._get_val(latest, "MOM5") or 0
            if ratio > 1.5:
                if pct_chg > 0:
                    signals.append({"indicator": "Volume", "value": f"{ratio:.1f}x avg",
                                     "signal": "Bullish", "description": "High volume on upward move — strong conviction", "score": 0.9, "weight": 0.8})
                else:
                    signals.append({"indicator": "Volume", "value": f"{ratio:.1f}x avg",
                                     "signal": "Bearish", "description": "High volume on downward move — strong selling", "score": -0.9, "weight": 0.8})
            elif ratio < 0.6:
                signals.append({"indicator": "Volume", "value": f"{ratio:.1f}x avg",
                                 "signal": "Neutral", "description": "Below-average volume — low conviction", "score": -0.1, "weight": 0.8})
            else:
                signals.append({"indicator": "Volume", "value": f"{ratio:.1f}x avg",
                                 "signal": "Neutral", "description": "Normal volume activity", "score": 0.0, "weight": 0.8})

        # Momentum
        mom10 = self._get_val(latest, "MOM10")
        if mom10 is not None:
            if mom10 > 8:
                signals.append({"indicator": "Momentum (10d)", "value": f"+{mom10:.1f}%",
                                 "signal": "Bullish", "description": "Strong positive 10-day momentum", "score": 0.9, "weight": 1.0})
            elif mom10 < -8:
                signals.append({"indicator": "Momentum (10d)", "value": f"{mom10:.1f}%",
                                 "signal": "Bearish", "description": "Strong negative 10-day momentum", "score": -0.9, "weight": 1.0})
            elif mom10 > 3:
                signals.append({"indicator": "Momentum (10d)", "value": f"+{mom10:.1f}%",
                                 "signal": "Bullish", "description": "Positive momentum", "score": 0.4, "weight": 1.0})
            elif mom10 < -3:
                signals.append({"indicator": "Momentum (10d)", "value": f"{mom10:.1f}%",
                                 "signal": "Bearish", "description": "Negative momentum", "score": -0.4, "weight": 1.0})
            else:
                signals.append({"indicator": "Momentum (10d)", "value": f"{mom10:+.1f}%",
                                 "signal": "Neutral", "description": "Flat momentum", "score": 0.0, "weight": 1.0})

        # Support / Resistance proximity
        pct_from_support = ((price - support) / support) * 100 if support > 0 else 100
        pct_from_resistance = ((resistance - price) / price) * 100 if price > 0 else 100
        if pct_from_support < 2:
            signals.append({"indicator": "Support/Resistance", "value": f"S: {support:.2f}",
                             "signal": "Bullish", "description": "Price at key support level — bounce likely", "score": 0.6, "weight": 0.6})
        elif pct_from_resistance < 2:
            signals.append({"indicator": "Support/Resistance", "value": f"R: {resistance:.2f}",
                             "signal": "Bearish", "description": "Price at key resistance — rejection possible", "score": -0.6, "weight": 0.6})
        else:
            signals.append({"indicator": "Support/Resistance", "value": f"S:{support:.2f} R:{resistance:.2f}",
                             "signal": "Neutral", "description": f"S/R gap: {pct_from_support:.1f}% below R, {pct_from_resistance:.1f}% above S", "score": 0.0, "weight": 0.6})

        return signals

    def _determine_trend(self, df, price) -> dict:
        last = df.dropna(subset=["SMA20"]).iloc[-1] if not df.dropna(subset=["SMA20"]).empty else df.iloc[-1]

        sma20 = self._get_val(last, "SMA20") or price
        sma50 = self._get_val(last, "SMA50") or price
        sma200 = self._get_val(last, "SMA200")

        short_term = "Bullish" if price > sma20 else "Bearish"
        medium_term = "Bullish" if price > sma50 else "Bearish"
        long_term = ("Bullish" if price > sma200 else "Bearish") if sma200 else "N/A (< 200 days data)"

        # 5-day direction
        recent = df["Close"].tail(6).pct_change().dropna()
        direction = "Rising" if recent.sum() > 0 else "Falling"

        bulls = sum(1 for t in [short_term, medium_term, long_term] if t == "Bullish")
        if bulls >= 2:
            desc = "Uptrend"
        elif bulls == 1:
            desc = "Mixed Trend"
        else:
            desc = "Downtrend"

        return {
            "short_term": short_term,
            "medium_term": medium_term,
            "long_term": long_term,
            "recent_direction": direction,
            "sma_aligned": sma20 > sma50 if sma50 else False,
            "description": desc,
        }

    # ── Chart Data ────────────────────────────────────────────────────────

    def _prepare_chart_data(self, df) -> dict:
        recent = df.tail(90)

        def to_list(series, decimals=2):
            return [round(float(v), decimals) if not pd.isna(v) else None for v in series]

        return {
            "dates": [d.strftime("%Y-%m-%d") for d in recent.index],
            "close": to_list(recent["Close"]),
            "open": to_list(recent["Open"]),
            "high": to_list(recent["High"]),
            "low": to_list(recent["Low"]),
            "volume": [int(v) for v in recent["Volume"]],
            "sma20": to_list(recent["SMA20"]),
            "sma50": to_list(recent["SMA50"]),
            "bb_upper": to_list(recent["BB_Upper"]),
            "bb_lower": to_list(recent["BB_Lower"]),
            "rsi": to_list(recent["RSI"], 1),
            "macd": to_list(recent["MACD"], 4),
            "macd_signal": to_list(recent["MACD_Signal"], 4),
            "macd_histogram": to_list(recent["MACD_Histogram"], 4),
        }

    # ── Helpers ───────────────────────────────────────────────────────────

    def _resolve_ticker(self, query: str) -> str:
        query_clean = query.strip().upper().replace("  ", " ")
        # Check manual map
        if query_clean in self.TICKER_MAP:
            return self.TICKER_MAP[query_clean]
        # Try as-is
        if self._ticker_valid(query_clean):
            return query_clean
        # Try .NS suffix (NSE India)
        if self._ticker_valid(query_clean + ".NS"):
            return query_clean + ".NS"
        # Try .BO suffix (BSE India)
        if self._ticker_valid(query_clean + ".BO"):
            return query_clean + ".BO"
        # yfinance search
        try:
            results = yf.Search(query, max_results=3)
            quotes = results.quotes
            if quotes:
                return quotes[0].get("symbol", query_clean)
        except Exception:
            pass
        return query_clean

    def _ticker_valid(self, ticker: str) -> bool:
        try:
            t = yf.Ticker(ticker)
            h = t.history(period="5d")
            return not h.empty
        except Exception:
            return False

    def _safe_info(self, stock) -> dict:
        try:
            return stock.info or {}
        except Exception:
            return {}

    def _safe_pct_change(self, df, days: int) -> float:
        if len(df) > days:
            chg = df["Close"].pct_change(days).iloc[-1] * 100
            return round(float(chg), 2) if not np.isnan(chg) else 0.0
        return 0.0

    def _get_val(self, row, col):
        try:
            v = row.get(col, np.nan)
            if v is None or (isinstance(v, float) and np.isnan(v)):
                return None
            return float(v)
        except Exception:
            return None

    def _round_safe(self, val, decimals=2):
        if val is None:
            return None
        try:
            return round(float(val), decimals)
        except Exception:
            return None

    def _calc_support_resistance(self, df, lookback=90) -> tuple:
        recent = df.tail(lookback)
        support = float(recent["Low"].quantile(0.08))
        resistance = float(recent["High"].quantile(0.92))
        return support, resistance

    def _assess_data_quality(self, df) -> dict:
        n = len(df)
        score = 100
        issues = []
        if n < 200:
            score -= 25
            issues.append(f"Only {n} trading days available; SMA-200 may be incomplete")
        if n < 50:
            score -= 30
            issues.append("Very limited history — analysis reliability is reduced")
        grade = "High" if score >= 80 else "Medium" if score >= 60 else "Low"
        return {"score": score, "records": n, "grade": grade, "issues": issues}
