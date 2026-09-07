"""
FinSight AI - News Intelligence Engine
Fetches, analyzes, and scores recent financial news using
keyword-weighted sentiment and pattern extraction.
"""

import os
import re
import requests
from datetime import datetime, timedelta


# ── Financial keyword lexicons ─────────────────────────────────────────────
POSITIVE_WORDS = [
    "growth", "profit", "revenue", "record", "beat", "surge", "rally",
    "bullish", "upgrade", "outperform", "gain", "rise", "expand", "innovation",
    "partnership", "acquisition", "positive", "strong", "breakthrough", "award",
    "dividend", "buyback", "launch", "approved", "patent", "recovery",
    "momentum", "optimistic", "exceed", "milestone", "boost",
]

NEGATIVE_WORDS = [
    "loss", "decline", "fall", "drop", "miss", "warning", "risk",
    "bearish", "downgrade", "underperform", "weak", "concern", "debt",
    "layoff", "investigation", "lawsuit", "recession", "crash", "plunge",
    "disappointing", "shortfall", "delay", "recall", "ban", "fine",
    "fraud", "bankruptcy", "selloff", "volatility", "uncertainty",
    "downgrade", "negative", "struggle", "contraction",
]

MAJOR_EVENT_KEYWORDS = [
    "earnings", "quarterly results", "merger", "acquisition", "ipo",
    "partnership", "lawsuit", "investigation", "dividend", "stock split",
    "ceo", "leadership", "guidance", "outlook", "forecast", "warning",
    "recall", "approval", "patent", "agreement", "contract",
]

THEME_MAP = {
    "Earnings & Revenue": ["earnings", "revenue", "profit", "quarterly", "annual", "eps", "results", "income"],
    "Product & Innovation": ["launch", "product", "new", "release", "announce", "introduce", "technology", "ai", "patent"],
    "Market Competition": ["competition", "rival", "market share", "competitor", "beats", "vs"],
    "Regulatory & Legal": ["regulatory", "sec", "ftc", "compliance", "lawsuit", "investigation", "fine", "ban", "approval"],
    "M&A & Partnerships": ["acquisition", "merger", "partnership", "deal", "agreement", "joint venture", "takeover"],
    "Leadership Changes": ["ceo", "cfo", "executive", "leadership", "appointed", "resigned", "board", "director"],
    "Macro Economy": ["inflation", "interest rate", "federal reserve", "economy", "recession", "gdp", "tariff", "fed"],
    "ESG & Sustainability": ["esg", "sustainability", "climate", "carbon", "green", "renewable", "diversity"],
}


class NewsIntelligenceEngine:

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY", "")
        self.base_url = "https://newsapi.org/v2/everything"

    def analyze(self, company_name: str, ticker: str) -> dict:
        articles_raw = self._fetch_news(company_name, ticker)

        if not articles_raw:
            return self._empty_result()

        analyzed = [self._analyze_article(a) for a in articles_raw[:25]]
        analyzed = [a for a in analyzed if a is not None]

        if not analyzed:
            return self._empty_result()

        scores = [a["sentiment_score"] for a in analyzed]
        avg_score = sum(scores) / len(scores)

        positive = [a for a in analyzed if a["sentiment"] == "Positive"]
        negative = [a for a in analyzed if a["sentiment"] == "Negative"]
        neutral = [a for a in analyzed if a["sentiment"] == "Neutral"]

        if avg_score > 0.12:
            overall = "Positive"
        elif avg_score < -0.12:
            overall = "Negative"
        else:
            overall = "Neutral"

        # Clamp news signal to [-1, 1]
        news_signal = max(-1.0, min(1.0, avg_score * 4.0))

        return {
            "articles": analyzed[:10],
            "total_articles": len(analyzed),
            "sentiment_score": round(avg_score, 3),
            "positive_count": len(positive),
            "negative_count": len(negative),
            "neutral_count": len(neutral),
            "overall_sentiment": overall,
            "positive_catalysts": self._extract_headlines(positive, 5),
            "negative_factors": self._extract_headlines(negative, 5),
            "major_events": self._extract_major_events(analyzed),
            "themes": self._extract_themes(analyzed),
            "news_signal": round(news_signal, 3),
            "data_available": True,
            "source_count": len(set(a.get("source", "") for a in analyzed)),
        }

    # ── Fetching ──────────────────────────────────────────────────────────

    def _fetch_news(self, company_name: str, ticker: str) -> list:
        if not self.api_key:
            return []

        # Use shorter ticker or company name to maximize results
        short_name = company_name.split()[0] if company_name else ticker
        query = f'"{short_name}" stock OR "{ticker}" shares'
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        try:
            resp = requests.get(
                self.base_url,
                params={
                    "q": query,
                    "from": from_date,
                    "sortBy": "relevancy",
                    "language": "en",
                    "pageSize": 30,
                    "apiKey": self.api_key,
                },
                timeout=12,
            )
            if resp.status_code == 200:
                return resp.json().get("articles", [])
            return []
        except Exception:
            return []

    # ── Sentiment Analysis ────────────────────────────────────────────────

    def _analyze_article(self, article: dict) -> dict | None:
        title = article.get("title", "") or ""
        desc = article.get("description", "") or ""
        if not title or title.lower() == "[removed]":
            return None

        text = f"{title} {desc}"
        score = self._score_text(text)

        if score > 0.12:
            label = "Positive"
        elif score < -0.12:
            label = "Negative"
        else:
            label = "Neutral"

        return {
            "title": title[:180],
            "source": article.get("source", {}).get("name", "Unknown"),
            "publishedAt": article.get("publishedAt", ""),
            "url": article.get("url", ""),
            "description": (desc[:200] if desc else ""),
            "sentiment": label,
            "sentiment_score": round(score, 3),
        }

    def _score_text(self, text: str) -> float:
        text_lower = text.lower()
        pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
        neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)

        # Normalize: each keyword contributes ~0.1
        raw = (pos - neg) * 0.09
        return max(-1.0, min(1.0, raw))

    # ── Extraction Helpers ────────────────────────────────────────────────

    def _extract_headlines(self, articles: list, n: int) -> list:
        return [a["title"] for a in articles[:n] if a.get("title")]

    def _extract_major_events(self, articles: list) -> list:
        events = []
        for a in articles:
            title_lower = (a.get("title", "") or "").lower()
            if any(kw in title_lower for kw in MAJOR_EVENT_KEYWORDS):
                events.append(a["title"])
        return events[:4]

    def _extract_themes(self, articles: list) -> list:
        all_text = " ".join(
            (a.get("title", "") or "") + " " + (a.get("description", "") or "")
            for a in articles
        ).lower()

        scored = []
        for theme, keywords in THEME_MAP.items():
            hits = sum(1 for k in keywords if k in all_text)
            if hits > 0:
                scored.append((theme, hits))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in scored[:5]]

    # ── Empty State ───────────────────────────────────────────────────────

    def _empty_result(self) -> dict:
        return {
            "articles": [],
            "total_articles": 0,
            "sentiment_score": 0.0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "overall_sentiment": "Neutral",
            "positive_catalysts": [],
            "negative_factors": [],
            "major_events": [],
            "themes": [],
            "news_signal": 0.0,
            "data_available": False,
            "source_count": 0,
        }
