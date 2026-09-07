"""
FinSight AI - Signal Fusion & Probability Engine
Combines technical and news signals using a transparent weighted-scoring
methodology to produce quantitative probability estimates.

METHODOLOGY (fully deterministic):
  1. Technical Score  = weighted average of individual indicator scores [-1, 1]
  2. News Score       = normalized news sentiment signal [-1, 1]
  3. Combined Score   = 0.70 × Technical + 0.30 × News  [-1, 1]
  4. Volatility Drag  = penalize combined score for extreme volatility
  5. Probability      = linear mapping of score → [15%, 85%] with vol-pull-to-50
  6. Scenarios        = historical-volatility-based price range estimates
"""

import math


# ── Indicator weights ─────────────────────────────────────────────────────
INDICATOR_WEIGHTS = {
    "SMA 200":          1.5,
    "SMA 50":           1.2,
    "MACD":             1.3,
    "RSI":              1.2,
    "SMA 20":           1.0,
    "Momentum (10d)":   1.0,
    "Volume":           0.8,
    "Bollinger Bands":  0.7,
    "Support/Resistance": 0.6,
}

TECH_WEIGHT  = 0.70
NEWS_WEIGHT  = 0.30


class SignalFusionEngine:

    def calculate(self, technical: dict, news: dict) -> dict:
        signals = technical.get("signals", [])
        tech_score = self._weighted_tech_score(signals)
        news_score = news.get("news_signal", 0.0)

        # Weighted fusion
        raw_combined = (tech_score * TECH_WEIGHT) + (news_score * NEWS_WEIGHT)

        # Volatility drag: high volatility pulls score toward 0 (more uncertainty)
        vol = technical.get("volatility_annualized", 25.0) or 25.0
        vol_drag = self._volatility_drag(vol)
        combined = max(-1.0, min(1.0, raw_combined - vol_drag))

        # Market outlook label
        outlook = self._outlook_label(combined, vol)

        # Probability estimates
        upside_prob, downside_prob = self._estimate_probabilities(combined, vol)

        # Price scenarios
        price = technical.get("current_price", 100.0) or 100.0
        bull_scenario = self._bullish_scenario(price, combined, vol)
        bear_scenario = self._bearish_scenario(price, combined, vol)

        # Risk level
        risk = self._risk_level(vol, combined, news)

        # Risk-reward
        rr = self._risk_reward(bull_scenario, bear_scenario, price)

        # Confidence
        confidence = self._confidence(technical, news)

        # Methodology breakdown (for Explainable AI)
        breakdown = self._score_breakdown(signals, tech_score, news_score, vol_drag, combined)

        return {
            "technical_score":      round(tech_score, 3),
            "news_score":           round(news_score, 3),
            "vol_drag":             round(vol_drag, 3),
            "combined_score":       round(combined, 3),
            "market_outlook":       outlook,
            "upside_probability":   round(upside_prob),
            "downside_probability": round(downside_prob),
            "bullish_scenario":     bull_scenario,
            "bearish_scenario":     bear_scenario,
            "risk_level":           risk,
            "risk_reward_ratio":    rr,
            "confidence":           confidence,
            "tech_weight_pct":      int(TECH_WEIGHT * 100),
            "news_weight_pct":      int(NEWS_WEIGHT * 100),
            "breakdown":            breakdown,
        }

    # ── Technical Score ────────────────────────────────────────────────────

    def _weighted_tech_score(self, signals: list) -> float:
        total_w = 0.0
        weighted_sum = 0.0
        for sig in signals:
            ind = sig.get("indicator", "")
            w = sig.get("weight") or INDICATOR_WEIGHTS.get(ind, 0.5)
            s = sig.get("score", 0.0)
            weighted_sum += s * w
            total_w += w
        return (weighted_sum / total_w) if total_w > 0 else 0.0

    # ── Volatility Drag ────────────────────────────────────────────────────

    def _volatility_drag(self, vol: float) -> float:
        """High volatility introduces uncertainty → penalize the score magnitude."""
        if vol <= 25:
            return 0.0
        elif vol <= 50:
            return (vol - 25) / 250   # 0 → 0.10
        else:
            return 0.10 + (vol - 50) / 200  # 0.10 → 0.35 for vol 50→120

    # ── Outlook Label ──────────────────────────────────────────────────────

    def _outlook_label(self, score: float, vol: float) -> str:
        if vol > 70:
            return "High Risk"
        if score >= 0.45:
            return "Strong Bullish"
        if score >= 0.15:
            return "Moderately Bullish"
        if score <= -0.45:
            return "High Risk"
        if score <= -0.15:
            return "Moderately Bearish"
        return "Neutral"

    # ── Probability Estimation ─────────────────────────────────────────────

    def _estimate_probabilities(self, score: float, vol: float) -> tuple:
        """
        Linear map: score -1 → 20%, score 0 → 50%, score +1 → 80%.
        Then pull toward 50% proportional to excess volatility.
        """
        base_upside = 50.0 + score * 30.0  # [-1,1] → [20%, 80%]

        # Volatility pull-to-center: >40% vol → gradually pull toward 50%
        if vol > 40:
            pull = min(0.55, (vol - 40) / 100.0)
            base_upside = base_upside * (1 - pull) + 50.0 * pull

        upside = max(15.0, min(85.0, base_upside))
        downside = 100.0 - upside
        return upside, downside

    # ── Scenario Calculations ──────────────────────────────────────────────

    def _bullish_scenario(self, price, score, vol) -> dict:
        monthly_vol = vol / math.sqrt(12)  # approx 1-month vol %
        boost = 1.0 + max(0.0, score) * 0.5
        base_up = monthly_vol * boost
        high_up = base_up * 1.6
        return {
            "low_target":  round(price * (1 + base_up / 100), 2),
            "high_target": round(price * (1 + high_up / 100), 2),
            "low_pct":     round(base_up, 1),
            "high_pct":    round(high_up, 1),
            "horizon":     "1–3 months",
            "basis":       f"1-month σ = {monthly_vol:.1f}%, score boost = {boost:.2f}x",
        }

    def _bearish_scenario(self, price, score, vol) -> dict:
        monthly_vol = vol / math.sqrt(12)
        boost = 1.0 + max(0.0, -score) * 0.5
        base_dn = monthly_vol * boost
        high_dn = base_dn * 1.6
        return {
            "low_target":  round(price * (1 - high_dn / 100), 2),
            "high_target": round(price * (1 - base_dn / 100), 2),
            "low_pct":     round(base_dn, 1),
            "high_pct":    round(high_dn, 1),
            "horizon":     "1–3 months",
            "basis":       f"1-month σ = {monthly_vol:.1f}%, risk boost = {boost:.2f}x",
        }

    # ── Risk Level ─────────────────────────────────────────────────────────

    def _risk_level(self, vol, score, news) -> dict:
        risk_pts = 0
        factors = []

        if vol > 65:
            risk_pts += 3; factors.append(f"Very high volatility ({vol:.0f}%)")
        elif vol > 40:
            risk_pts += 2; factors.append(f"High volatility ({vol:.0f}%)")
        elif vol > 25:
            risk_pts += 1; factors.append(f"Above-average volatility ({vol:.0f}%)")

        if score < -0.5:
            risk_pts += 2; factors.append("Strongly bearish signal alignment")
        elif score < -0.15:
            risk_pts += 1; factors.append("Moderately bearish signal alignment")

        neg = news.get("negative_count", 0)
        total = news.get("total_articles", 1) or 1
        if (neg / total) > 0.5:
            risk_pts += 2; factors.append("Majority of news is negative")
        elif (neg / total) > 0.3:
            risk_pts += 1; factors.append("Notable negative news presence")

        if risk_pts >= 5:
            level, color = "Very High", "#ef4444"
        elif risk_pts >= 3:
            level, color = "High", "#f97316"
        elif risk_pts >= 2:
            level, color = "Medium", "#eab308"
        elif risk_pts >= 1:
            level, color = "Low-Medium", "#3b82f6"
        else:
            level, color = "Low", "#10b981"

        return {"level": level, "color": color, "score": risk_pts, "factors": factors}

    # ── Risk-Reward ────────────────────────────────────────────────────────

    def _risk_reward(self, bull, bear, price) -> str:
        upside = bull["high_target"] - price
        downside = price - bear["low_target"]
        if downside <= 0:
            return "∞"
        return f"{(upside / downside):.2f}:1"

    # ── Confidence ─────────────────────────────────────────────────────────

    def _confidence(self, technical, news) -> dict:
        dq = technical.get("data_quality", {}).get("score", 80)
        has_news = news.get("data_available", False)
        n_articles = news.get("total_articles", 0)

        if dq >= 80 and has_news and n_articles >= 5:
            return {"level": "High", "pct": 85,
                    "note": "Sufficient historical data + recent news available"}
        elif dq >= 60 and (has_news or dq >= 75):
            return {"level": "Medium", "pct": 65,
                    "note": "Moderate data quality — estimates may have wider error bands"}
        else:
            return {"level": "Low", "pct": 40,
                    "note": "Limited data — treat all estimates with caution"}

    # ── Breakdown (Explainable AI) ─────────────────────────────────────────

    def _score_breakdown(self, signals, tech_score, news_score, vol_drag, combined) -> list:
        rows = []
        for sig in signals:
            rows.append({
                "indicator": sig.get("indicator"),
                "signal":    sig.get("signal"),
                "raw_score": sig.get("score", 0),
                "weight":    sig.get("weight") or INDICATOR_WEIGHTS.get(sig.get("indicator", ""), 0.5),
            })
        rows.append({"indicator": "Technical Composite", "signal": "—", "raw_score": round(tech_score, 3), "weight": TECH_WEIGHT})
        rows.append({"indicator": "News Sentiment",       "signal": "—", "raw_score": round(news_score, 3), "weight": NEWS_WEIGHT})
        rows.append({"indicator": "Volatility Drag",      "signal": "—", "raw_score": round(-vol_drag, 3),  "weight": 1.0})
        rows.append({"indicator": "FINAL COMBINED SCORE", "signal": "—", "raw_score": round(combined, 3),   "weight": 1.0})
        return rows
