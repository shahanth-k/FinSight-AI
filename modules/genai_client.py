"""Thin wrapper around the Google Gemini API used by FinSight AI.

Responsibilities:
- Read the API key and model name from environment variables (never hard-coded).
- Build a google-genai Client.
- Send the structured prompt and return the raw text response.
- Raise a clear, catchable error on API failure.

Migrated from the deprecated `google-generativeai` SDK to `google-genai`.
"""

from __future__ import annotations

import os
from typing import Optional

from google import genai
from google.genai import types


class GeminiConfigError(RuntimeError):
    """Raised when the Gemini API key is missing or configuration is invalid."""


class GeminiAPIError(RuntimeError):
    """Raised when the Gemini API call itself fails."""


def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiConfigError(
            "GEMINI_API_KEY is not set. Add it to your .env file or environment "
            "before running FinSight AI."
        )
    return api_key


def _get_model_name() -> str:
    # gemini-flash-latest always resolves to the latest stable Flash model.
    return (
        os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip() or "gemini-flash-latest"
    )


def generate_analysis(prompt: str, system_instruction: Optional[str] = None) -> str:
    """Send *prompt* to Gemini and return the raw text response.

    Uses the new google-genai SDK (google.genai).
    Raises GeminiConfigError or GeminiAPIError on failure.
    """
    try:
        api_key = _get_api_key()
    except GeminiConfigError:
        raise
    except Exception as exc:  # pragma: no cover
        raise GeminiConfigError(str(exc)) from exc

    try:
        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            temperature=0.3,
            top_p=0.9,
            max_output_tokens=2048,
            system_instruction=system_instruction or None,
        )
        response = client.models.generate_content(
            model=_get_model_name(),
            contents=prompt,
            config=config,
        )
    except Exception as exc:
        raise GeminiAPIError(f"Gemini API call failed: {exc}") from exc

    text = response.text if response and response.text else None
    if not text:
        raise GeminiAPIError("Gemini returned an empty response.")
    return text