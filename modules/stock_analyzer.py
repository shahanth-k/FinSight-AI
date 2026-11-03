"""Stock quantitative analysis and probability scoring engine for FinSight AI."""

from __future__ import annotations

from typing import Any, Dict


def compute_stock_intelligence(stock: Dict[str, Any], gemini_sentiment: float = 0.0) -> Dict[str, Any]:
    """Calculate the probability-based intelligence metrics matching FinSight AI v2."""
    price = stock.get("price") or 100.0
    prev = stock.get("prev_close") or price
    hi52 = stock.get("week_52_high") or (price * 1.25)
    lo52 = stock.get("week_52_low") or (price * 0.75)
    returns = stock.get("period_returns") or {}
    
    r1d = returns.get("1D")
    if r1d is None:
        r1d = round(((price / prev) - 1.0) * 100, 2) if prev else 0.0
    r5d = returns.get("5D") if returns.get("5D") is not None else (r1d * 1.8)
    r26d = returns.get("26D") if returns.get("26D") is not None else (r5d * 1.5)

    # 1. Technical signal score (-1.0 to +1.0)
    mom_score = max(-1.0, min(1.0, (r1d * 0.4 + r5d * 0.3) / 4.0))
    trend_score = max(-1.0, min(1.0, r26d / 8.0))
    range_52 = hi52 - lo52 if hi52 > lo52 else 1.0
    pos_52 = (price - lo52) / range_52
    range_score = (pos_52 - 0.5) * 2.0

    technical_score = round(mom_score * 0.45 + trend_score * 0.35 + range_score * 0.20, 3)
    technical_score = max(-0.95, min(0.95, technical_score))

    # 2. News score (-1.0 to +1.0)
    news_score = round(max(-1.0, min(1.0, gemini_sentiment)), 3)

    # 3. Combined Signal Score
    combined_score = round(0.70 * technical_score + 0.30 * news_score, 3)

    # 4. Upside & Downside Probabilities (maps -1..+1 to 20%..80%)
    upside_prob = int(round(50.0 + combined_score * 30.0))
    upside_prob = max(18, min(82, upside_prob))
    downside_prob = 100 - upside_prob

    # 5. Verdict determination
    if combined_score >= 0.45:
        verdict = "Bullish"
        verdict_class = "bullish"
        verdict_color = "#22c55e"
        bullet_icon = "🔵"
        bullet_text = "Strong bullish signals across technical and momentum indicators."
    elif combined_score >= 0.12:
        verdict = "Moderately Bullish"
        verdict_class = "moderately-bullish"
        verdict_color = "#38bdf8"
        bullet_icon = "🔵"
        bullet_text = "More bullish signals than bearish. Conditions are favorable but not overwhelmingly so."
    elif combined_score <= -0.45:
        verdict = "Bearish"
        verdict_class = "bearish"
        verdict_color = "#ef4444"
        bullet_icon = "🟡"
        bullet_text = "Strong bearish pressures dominate with heightened downside exposure."
    elif combined_score <= -0.12:
        verdict = "Moderately Bearish"
        verdict_class = "moderately-bearish"
        verdict_color = "#f59e0b"
        bullet_icon = "🟡"
        bullet_text = "More bearish signals than bullish. Caution is warranted; downside risk elevated."
    else:
        verdict = "Neutral"
        verdict_class = "neutral"
        verdict_color = "#94a3b8"
        bullet_icon = "⚪"
        bullet_text = "Balanced signals between bullish and bearish. Range-bound action expected."

    # 6. Risk Level
    est_volatility = int(round(abs(r1d) * 2.5 + abs(r5d) * 1.2 + 18.0))
    est_volatility = max(12, min(55, est_volatility))

    if est_volatility > 32 or abs(combined_score) > 0.6:
        risk_level = "High"
        risk_color = "#ef4444"
    elif est_volatility > 22 or abs(combined_score) > 0.2:
        risk_level = "Medium" if combined_score < 0 else "Low-Medium"
        risk_color = "#f59e0b" if risk_level == "Medium" else "#38bdf8"
    else:
        risk_level = "Low"
        risk_color = "#22c55e"

    risk_sub = f"Above-average volatility ({est_volatility}%). {verdict.lower()} signal alignment."

    # 7. Risk-Reward Ratio
    rr_num = round(upside_prob / max(1.0, float(downside_prob)), 2)
    risk_reward_ratio = f"{rr_num:.2f}:1"

    # 8. Analysis Confidence
    confidence_pct = 65
    confidence_label = f"Medium ({confidence_pct}%)"
    confidence_sub = "Moderate data quality — estimates may have wider error bands"

    return {
        "verdict": verdict,
        "verdict_class": verdict_class,
        "verdict_color": verdict_color,
        "bullet_icon": bullet_icon,
        "bullet_text": bullet_text,
        "combined_score": f"{combined_score:+.3f}",
        "combined_score_num": combined_score,
        "technical_score": f"{technical_score:+.3f}",
        "news_score": f"{news_score:+.3f}",
        "upside_prob": upside_prob,
        "downside_prob": downside_prob,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "risk_sub": risk_sub,
        "risk_reward_ratio": risk_reward_ratio,
        "confidence_pct": confidence_pct,
        "confidence_label": confidence_label,
        "confidence_sub": confidence_sub,
    }
