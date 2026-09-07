"""
FinSight AI - Gemini AI Synthesizer
Uses Google Gemini to synthesize pre-calculated quantitative findings
into a professional human-readable intelligence report.

ROLE: Gemini does NOT predict prices. It synthesizes, explains, and narrativizes
the structured data already produced by the deterministic engines.
"""

import os
import json
import re

try:
    from google import genai as new_genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GeminiSynthesizer:

    def __init__(self):
        self.client = None
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key and GENAI_AVAILABLE:
            try:
                self.client = new_genai.Client(api_key=api_key)
            except Exception as e:
                print(f"[Gemini] Init failed: {e}")

    def synthesize(self, technical: dict, news: dict, fusion: dict) -> dict:
        if not self.client:
            return self._rule_based_synthesis(technical, news, fusion)

        prompt = self._build_prompt(technical, news, fusion)
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"temperature": 0.35, "max_output_tokens": 1200},
            )
            return self._parse_gemini_response(response.text, technical, news, fusion)
        except Exception as e:
            print(f"[Gemini] Generation error: {e}")
            return self._rule_based_synthesis(technical, news, fusion)

    # ── Prompt Construction ────────────────────────────────────────────────

    def _build_prompt(self, technical: dict, news: dict, fusion: dict) -> str:
        ticker = technical.get("ticker", "UNKNOWN")
        company = technical.get("company_name", ticker)
        price = technical.get("current_price", 0)
        rsi = technical.get("rsi", 50) or 50
        macd = technical.get("macd", 0) or 0
        macd_sig = technical.get("macd_signal", 0) or 0
        trend = technical.get("trend", {})
        vol = technical.get("volatility_annualized", 30) or 30
        signals = technical.get("signals", [])

        sig_lines = "\n".join(
            f"  • {s['indicator']}: {s['signal']} — {s['description']} (score: {s['score']:.1f})"
            for s in signals
        )

        outlook = fusion.get("market_outlook", "Neutral")
        upside_p = fusion.get("upside_probability", 50)
        downside_p = fusion.get("downside_probability", 50)
        risk = fusion.get("risk_level", {}).get("level", "Medium")
        rr = fusion.get("risk_reward_ratio", "N/A")
        bull = fusion.get("bullish_scenario", {})
        bear = fusion.get("bearish_scenario", {})
        combined_score = fusion.get("combined_score", 0)
        tech_score = fusion.get("technical_score", 0)
        news_score = fusion.get("news_score", 0)

        pos_cats = news.get("positive_catalysts", [])[:3]
        neg_facs = news.get("negative_factors", [])[:3]
        themes = news.get("themes", [])

        return f"""You are FinSight AI, a professional financial intelligence synthesis engine.
Your task: Analyze the PRE-CALCULATED quantitative data below and write a structured JSON intelligence report.

CRITICAL RULES:
- You are EXPLAINING the system's pre-calculated numbers, NOT making new predictions
- Never guarantee outcomes. Always use probabilistic language ("suggests", "indicates", "based on patterns")
- Be specific — cite the actual indicator values given below
- Be professional, analytical, and concise
- Output ONLY valid JSON, no markdown, no preamble

====== STRUCTURED DATA PACKAGE ======

Company: {company} ({ticker})
Current Price: {price}
Sector: {technical.get('sector', 'N/A')} | Industry: {technical.get('industry', 'N/A')}

--- PRICE PERFORMANCE ---
1-Day Change: {technical.get('price_change_1d', 0):.2f}%
5-Day Change: {technical.get('price_change_5d', 0):.2f}%
20-Day Change: {technical.get('price_change_20d', 0):.2f}%
52-Week High: {technical.get('week_52_high', 'N/A')} | 52-Week Low: {technical.get('week_52_low', 'N/A')}

--- TECHNICAL INDICATORS ---
RSI (14): {rsi:.1f} {'[OVERBOUGHT >70]' if rsi > 70 else '[OVERSOLD <30]' if rsi < 30 else '[NEUTRAL]'}
MACD: {macd:.4f} vs Signal: {macd_sig:.4f} ({'Bullish Cross' if macd > macd_sig else 'Bearish Cross'})
Trend: Short={trend.get('short_term','N/A')}, Medium={trend.get('medium_term','N/A')}, Long={trend.get('long_term','N/A')}
Overall Trend: {trend.get('description','N/A')}
Annualized Volatility: {vol:.1f}% {'[HIGH RISK ZONE]' if vol > 50 else ''}
Support: {technical.get('support', 'N/A')} | Resistance: {technical.get('resistance', 'N/A')}
ATR%: {technical.get('atr_pct', 'N/A')}%

--- ALL SIGNALS GENERATED ---
{sig_lines}

--- NEWS INTELLIGENCE ---
Articles analyzed: {news.get('total_articles', 0)} from {news.get('source_count', 0)} sources (last 30 days)
Sentiment: Positive={news.get('positive_count',0)}, Negative={news.get('negative_count',0)}, Neutral={news.get('neutral_count',0)}
Overall News Sentiment: {news.get('overall_sentiment','Neutral')} (score: {news.get('sentiment_score',0):.3f})
Major Themes: {', '.join(themes) if themes else 'No prominent themes'}
Top Positive Headlines: {' | '.join(pos_cats) if pos_cats else 'None'}
Top Negative Headlines: {' | '.join(neg_facs) if neg_facs else 'None'}

--- SYSTEM PROBABILITY ASSESSMENT (Pre-calculated) ---
Technical Score: {tech_score:.3f} (weight: 70%)
News Score: {news_score:.3f} (weight: 30%)
Combined Score: {combined_score:.3f} [-1 = extreme bearish, +1 = extreme bullish]
Market Outlook: {outlook}
Upside Probability: {upside_p}% | Downside Probability: {downside_p}%
Risk Level: {risk}
Risk-Reward Ratio: {rr}
Bullish Target Range: {bull.get('low_target','N/A')} – {bull.get('high_target','N/A')} (+{bull.get('low_pct','N/A')}% to +{bull.get('high_pct','N/A')}%)
Bearish Target Range: {bear.get('low_target','N/A')} – {bear.get('high_target','N/A')} (-{bear.get('low_pct','N/A')}% to -{bear.get('high_pct','N/A')}%)
Data Quality: {technical.get('data_quality',{}).get('grade','N/A')} | Confidence: {fusion.get('confidence',{}).get('level','N/A')}

====== END OF DATA ======

Return a JSON object with EXACTLY these fields:
{{
  "executive_summary": "2-3 sentence summary of the overall market situation for {company} — cite specific price levels and indicator values",
  "technical_narrative": "3-4 sentences synthesizing what the technical indicators collectively reveal. Be specific about RSI, MACD, trend alignment, and key signals",
  "news_narrative": "2-3 sentences summarizing the news environment and what impact it has on the technical picture",
  "opportunity_analysis": "2-3 sentences about what bullish evidence suggests in terms of potential opportunity if signals sustain",
  "risk_analysis": "2-3 sentences about the key risks — volatility, conflicting signals, negative catalysts",
  "explainability": "3-4 sentences precisely explaining WHY the combined score of {combined_score:.3f} was generated and HOW that maps to the {upside_p}% upside probability — be specific about which indicators drove the result",
  "key_signals": ["list of 5 most important signals currently active for this stock"],
  "positive_catalysts": ["list of 3 positive catalysts identified from news or technical patterns"],
  "risk_factors": ["list of 3 key risk factors from the analysis"],
  "investor_note": "1 sentence professional disclaimer emphasizing the probabilistic nature of this analysis"
}}"""

    # ── Response Parsing ───────────────────────────────────────────────────

    def _parse_gemini_response(self, text: str, technical: dict, news: dict, fusion: dict) -> dict:
        try:
            # Strip markdown fences if present
            clean = re.sub(r"```(?:json)?\s*", "", text).strip()
            data = json.loads(clean)
            data["success"] = True
            data["source"] = "gemini"
            return data
        except Exception:
            return self._rule_based_synthesis(technical, news, fusion)

    # ── Rule-Based Fallback ────────────────────────────────────────────────

    def _rule_based_synthesis(self, technical: dict, news: dict, fusion: dict) -> dict:
        ticker = technical.get("ticker", "this stock")
        company = technical.get("company_name", ticker)
        outlook = fusion.get("market_outlook", "Neutral")
        upside_p = fusion.get("upside_probability", 50)
        downside_p = fusion.get("downside_probability", 50)
        combined = fusion.get("combined_score", 0)
        risk = fusion.get("risk_level", {}).get("level", "Medium")
        rsi = technical.get("rsi", 50) or 50
        vol = technical.get("volatility_annualized", 30) or 30
        macd = technical.get("macd", 0) or 0
        macd_sig = technical.get("macd_signal", 0) or 0
        trend = technical.get("trend", {})
        news_sent = news.get("overall_sentiment", "Neutral")
        tech_score = fusion.get("technical_score", 0)
        news_score = fusion.get("news_score", 0)
        price = technical.get("current_price", 0)

        macd_state = "bullish crossover" if macd > macd_sig else "bearish crossover"
        rsi_state = "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral zone"
        trend_desc = trend.get("description", "Mixed")

        signals_driving = []
        for sig in technical.get("signals", []):
            if abs(sig.get("score", 0)) >= 0.7:
                signals_driving.append(f"{sig['indicator']} ({sig['signal']})")

        return {
            "success": True,
            "source": "rule_based",
            "executive_summary": (
                f"{company} ({ticker}) is trading at {price} with a {outlook} market outlook. "
                f"The FinSight AI quantitative engine calculates a {upside_p}% upside probability "
                f"based on a combined signal score of {combined:.3f}, reflecting {trend_desc.lower()} price action "
                f"and {news_sent.lower()} news sentiment."
            ),
            "technical_narrative": (
                f"The technical picture shows a {trend_desc.lower()} with {trend.get('short_term','N/A')} short-term "
                f"and {trend.get('medium_term','N/A')} medium-term trends. "
                f"RSI at {rsi:.1f} places the stock in the {rsi_state}, while MACD signals a {macd_state}. "
                f"Annualized volatility of {vol:.1f}% introduces {'significant' if vol > 40 else 'moderate'} uncertainty "
                f"to the outlook."
            ),
            "news_narrative": (
                f"The news environment over the past 30 days shows {news_sent.lower()} sentiment "
                f"across {news.get('total_articles', 0)} analyzed articles. "
                f"{'Positive news catalysts are reinforcing the bullish technical signals.' if news_sent == 'Positive' else 'Negative news sentiment is adding pressure on top of the technical signals.' if news_sent == 'Negative' else 'Neutral news sentiment has limited additional impact on the technical picture.'}"
            ),
            "opportunity_analysis": (
                f"If the {trend_desc.lower()} momentum sustains, the bullish scenario targets "
                f"{fusion.get('bullish_scenario',{}).get('low_pct','N/A')}%–{fusion.get('bullish_scenario',{}).get('high_pct','N/A')}% upside "
                f"over 1–3 months based on historical volatility patterns. "
                f"{'Strong signal alignment across multiple indicators increases conviction.' if tech_score > 0.3 else 'However, mixed signals require confirmation before high-conviction positioning.'}"
            ),
            "risk_analysis": (
                f"Risk is assessed as {risk} with annualized volatility of {vol:.1f}%. "
                f"Downside probability is {downside_p}%, with a bearish scenario projecting "
                f"{fusion.get('bearish_scenario',{}).get('low_pct','N/A')}%–{fusion.get('bearish_scenario',{}).get('high_pct','N/A')}% loss "
                f"if negative momentum materializes. "
                f"{'Negative news adds to downside pressure.' if news_sent == 'Negative' else 'News risk remains moderate.'}"
            ),
            "explainability": (
                f"The combined score of {combined:.3f} was derived from a technical composite of {tech_score:.3f} "
                f"(70% weight) and a news signal of {news_score:.3f} (30% weight). "
                f"{'Key drivers: ' + ', '.join(signals_driving[:3]) + '.' if signals_driving else ''} "
                f"This score was mapped to {upside_p}% upside probability using a linear scale "
                f"(score -1 = 20%, 0 = 50%, +1 = 80%), then adjusted for {vol:.0f}% annualized volatility, "
                f"which pulled the estimate slightly toward 50% to reflect higher uncertainty."
            ),
            "key_signals": [
                f"RSI: {rsi:.1f} ({rsi_state})",
                f"MACD: {macd_state}",
                f"Trend: {trend_desc}",
                f"Volatility: {vol:.1f}% annualized",
                f"News: {news_sent} sentiment",
            ],
            "positive_catalysts": (
                news.get("positive_catalysts", ["No positive news catalysts identified"])[:3]
                or ["Technical trend direction", "Volume pattern confirmation", "Momentum signals"]
            ),
            "risk_factors": (
                news.get("negative_factors", [])[:3]
                or [f"High volatility ({vol:.0f}%)", "Uncertain market conditions", "Signal divergence risk"]
            ),
            "investor_note": (
                "This analysis presents probability-based estimates derived from historical price patterns "
                "and available information — not guarantees of future returns. Always consult a qualified "
                "financial advisor before making investment decisions."
            ),
        }
