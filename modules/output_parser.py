"""Parse Gemini's raw response into a clean structured dict for the UI."""

from __future__ import annotations

import html
import json
import re
from typing import Any, Dict


class ResponseParseError(ValueError):
    """Raised when the Gemini response cannot be parsed into the expected shape."""


VALID_SENTIMENTS = {"Bullish", "Bearish", "Neutral"}


def _strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` fences if the model wrapped its JSON in them."""
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return text.strip()


def _coerce_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _coerce_str_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return [_coerce_str(item) for item in value if _coerce_str(item)]
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return [_coerce_str(value)]


def _coerce_jargon(value: Any) -> list:
    items: list = []
    if not isinstance(value, list):
        return items
    for entry in value:
        if isinstance(entry, dict):
            term = _coerce_str(entry.get("term"))
            expl = _coerce_str(entry.get("explanation"))
            if term:
                # FIX Bug 2: keep entries with a valid term even if explanation is empty
                items.append({
                    "term": term,
                    "explanation": expl or "No explanation provided.",
                })
        elif isinstance(entry, str) and entry.strip():
            items.append({"term": entry.strip(), "explanation": "No explanation provided."})
    return items


def _safe(text: str) -> str:
    """HTML-escape a string so it is safe to inject into unsafe_allow_html markup."""
    return html.escape(text)


def _empty_result() -> Dict[str, Any]:
    return {
        "summary": "",
        "sentiment": "Neutral",
        "reasoning": "",
        "jargon": [],
        "takeaways": {"positives": [], "risks": []},
    }


def parse_analysis_response(raw_text: str) -> Dict[str, Any]:
    """Parse the model's raw output into the canonical structured dict.

    Tolerates minor formatting drift (markdown fences, extra prose).
    Uses json.JSONDecoder.raw_decode to find the first complete JSON object
    so that multiple objects or stray prefix text don't crash the parser.
    """
    if not raw_text or not raw_text.strip():
        raise ResponseParseError("Empty response from the model.")

    cleaned = _strip_code_fences(raw_text)

    # FIX Bug 1 & 3: use raw_decode to reliably find the FIRST complete JSON
    # object, regardless of surrounding text or multiple JSON blobs.
    decoder = json.JSONDecoder()
    start = cleaned.find("{")
    if start == -1:
        raise ResponseParseError("No JSON object found in the model response.")

    try:
        data, _ = decoder.raw_decode(cleaned, start)
    except json.JSONDecodeError as exc:
        # Last-ditch: try decoding the entire cleaned string from the start
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            raise ResponseParseError(
                f"Model response was not valid JSON: {exc}"
            ) from exc

    if not isinstance(data, dict):
        raise ResponseParseError("Model response JSON was not an object.")

    result = _empty_result()

    result["summary"] = _coerce_str(data.get("summary"))
    sentiment = _coerce_str(data.get("sentiment"), default="Neutral")
    # Normalise casing/whitespace.
    sentiment_key = sentiment.strip().capitalize()
    if sentiment_key not in VALID_SENTIMENTS:
        # Try exact match ignoring case.
        match = next(
            (s for s in VALID_SENTIMENTS if s.lower() == sentiment.lower()), None
        )
        sentiment_key = match or "Neutral"
    result["sentiment"] = sentiment_key

    result["reasoning"] = _coerce_str(data.get("reasoning"))
    result["jargon"] = _coerce_jargon(data.get("jargon"))

    takeaways = data.get("takeaways")
    if isinstance(takeaways, dict):
        result["takeaways"] = {
            "positives": _coerce_str_list(takeaways.get("positives")),
            "risks": _coerce_str_list(takeaways.get("risks")),
        }
    else:
        result["takeaways"] = {"positives": [], "risks": []}

    return result