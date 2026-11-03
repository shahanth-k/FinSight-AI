"""FinSight AI — Streamlit entry point.

Single-page web app:
  1. User pastes a financial news article (or picks an example).
  2. App builds a structured prompt and calls the Gemini API.
  3. Results dashboard shows Summary, Sentiment (+ reasoning),
     Jargon explained, and Key Takeaways, with a persistent disclaimer.
"""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

import html as _html

from modules.genai_client import (
    GeminiAPIError,
    GeminiConfigError,
    generate_analysis,
)
from modules.output_parser import ResponseParseError, parse_analysis_response
from modules.prompt_templates import SYSTEM_INSTRUCTION, build_analysis_prompt


def _e(text: str) -> str:
    """HTML-escape a string for safe injection into unsafe_allow_html markup."""
    return _html.escape(str(text) if text else "")


load_dotenv()

APP_TITLE = "FinSight AI"
APP_TAGLINE = (
    "Generative AI-Powered Financial News Summarizer & Sentiment Insight Assistant"
)
DISCLAIMER = (
    "Educational use only. FinSight AI summarises and explains the article you "
    "paste; it does NOT provide financial, investment, or trading advice and "
    "does NOT use live market data."
)
MIN_ARTICLE_CHARS = 30

EXAMPLES = {
    "Bullish — Apple beats estimates": (
        "Apple today reported quarterly revenue of $94.8 billion, up 6% "
        "year-over-year, beating analyst estimates. iPhone sales grew, the "
        "Services segment hit an all-time high, and gross margin expanded "
        "to 46.3%. The company also raised its guidance for the next "
        "quarter above Street consensus."
    ),
    "Bearish — layoffs and missed targets": (
        "NovaCorp announced a 12% workforce reduction and cut its full-year "
        "revenue guidance after Q3 results missed analyst expectations. "
        "Free cash flow turned negative, EBITDA margin compressed by 380 "
        "basis points, and management blamed weaker enterprise demand and "
        "unfavourable FX."
    ),
    "Neutral — routine update": (
        "The Central Bank kept its policy rate unchanged at 5.25% in line "
        "with market expectations. The accompanying statement reiterated "
        "the data-dependent approach and made no forward commitments. "
        "Bond yields and the currency moved little in early trade."
    ),
}


def _inject_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: linear-gradient(180deg, #0b1f3a 0%, #0e2a52 35%, #0f3060 100%); }
        [data-testid="stAppViewContainer"] > .main { padding-top: 1.2rem; }
        section.main > div.block-container { padding-top: 1rem; max-width: 1100px; }
        h1, h2, h3, h4 { color: #f3f6fb !important; }
        [data-testid="stCaptionContainer"] p,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li { color: #e6ecf5 !important; }
        label, .stTextArea label { color: #f3f6fb !important; }

        .fs-hero {
            background: linear-gradient(135deg, #1f3a68 0%, #2e86c1 100%);
            padding: 1.4rem 1.6rem; border-radius: 14px; margin-bottom: 1rem;
            box-shadow: 0 6px 18px rgba(0,0,0,0.25);
        }
        .fs-hero h1 { margin: 0; font-size: 1.9rem; color: #fff !important; }
        .fs-hero p  { margin: 0.25rem 0 0; color: #dceaff !important; }

        .fs-card {
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 12px; padding: 1rem 1.1rem; margin-bottom: 0.8rem;
        }
        .fs-card h4 { margin: 0 0 0.4rem 0; color: #f3f6fb !important; }
        .fs-card p, .fs-card li { color: #e6ecf5 !important; }

        .fs-chip {
            display: inline-block; padding: 0.18rem 0.65rem; border-radius: 999px;
            font-weight: 700; font-size: 0.85rem; letter-spacing: 0.3px;
        }
        .fs-chip-bullish { background: #1f7a4d; color: #eafff3; }
        .fs-chip-bearish { background: #8a2a2a; color: #ffeaea; }
        .fs-chip-neutral { background: #4a5b7a; color: #eef2ff; }

        .fs-strip {
            background: rgba(255, 215, 0, 0.10);
            border-left: 4px solid #f1c40f;
            padding: 0.6rem 0.9rem; border-radius: 8px; margin: 0.6rem 0 1rem 0;
            color: #fff7d6 !important;
        }

        .fs-footer { text-align: center; color: #b9c4d6 !important; font-size: 0.85em; margin-top: 1rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _init_session_state() -> None:
    st.session_state.setdefault("analysis", None)
    st.session_state.setdefault("last_error", None)
    st.session_state.setdefault("article_text", "")


def _render_header() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="F",
        layout="wide",
    )
    _inject_theme()
    st.markdown(
        f"""
        <div class="fs-hero">
            <h1>{APP_TITLE}</h1>
            <p>{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='fs-strip'>⚠️ {DISCLAIMER}</div>", unsafe_allow_html=True)


def _validate_article(article: str) -> str | None:
    article = (article or "").strip()
    if not article:
        return "Please paste a financial news article into the text box before clicking Analyze."
    if len(article) < MIN_ARTICLE_CHARS:
        return (
            f"The article looks too short to analyze (minimum {MIN_ARTICLE_CHARS} "
            "characters). Please paste a complete article."
        )
    return None


def _sentiment_chip(label: str) -> str:
    key = {"Bullish": "bullish", "Bearish": "bearish", "Neutral": "neutral"}.get(
        label, "neutral"
    )
    return f"<span class='fs-chip fs-chip-{key}'>{label}</span>"


def _render_results(result: dict) -> None:
    summary = result.get("summary", "").strip()
    sentiment = result.get("sentiment", "Neutral")
    reasoning = result.get("reasoning", "").strip()
    jargon = result.get("jargon", []) or []
    takeaways = result.get("takeaways", {}) or {}
    positives = takeaways.get("positives", []) or []
    risks = takeaways.get("risks", []) or []

    tab_summary, tab_sentiment, tab_jargon, tab_takeaways = st.tabs(
        ["Summary", "Sentiment", "Jargon Explained", "Key Takeaways"]
    )

    with tab_summary:
        st.markdown(
            f"<div class='fs-card'><h4>Article Summary</h4>"
            f"<p>{_e(summary) or 'The model did not return a summary for this article.'}</p></div>",
            unsafe_allow_html=True,
        )

    with tab_sentiment:
        st.markdown(
            f"<div class='fs-card'><h4>Verdict</h4>{_sentiment_chip(sentiment)}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='fs-card'><h4>Reasoning</h4>"
            f"<p>{_e(reasoning) or 'No reasoning was provided by the model for this article.'}</p></div>",
            unsafe_allow_html=True,
        )

    with tab_jargon:
        if jargon:
            items = "".join(
                f"<li><b>{_e(e.get('term','').strip())}</b> — "
                f"{_e(e.get('explanation','').strip()) or 'No explanation provided.'}</li>"
                for e in jargon
            )
            st.markdown(
                f"<div class='fs-card'><h4>Jargon Explained</h4><ul>{items}</ul></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='fs-card'>No financial jargon was detected in this article.</div>",
                unsafe_allow_html=True,
            )

    with tab_takeaways:
        col_pos, col_risk = st.columns(2)
        with col_pos:
            items = (
                "".join(f"<li>{_e(x)}</li>" for x in positives)
                or "<li>None identified in the article.</li>"
            )
            st.markdown(
                f"<div class='fs-card'><h4>Positives</h4><ul>{items}</ul></div>",
                unsafe_allow_html=True,
            )
        with col_risk:
            items = (
                "".join(f"<li>{_e(x)}</li>" for x in risks)
                or "<li>None identified in the article.</li>"
            )
            st.markdown(
                f"<div class='fs-card'><h4>Risks</h4><ul>{items}</ul></div>",
                unsafe_allow_html=True,
            )


def main() -> None:
    _init_session_state()
    _render_header()

    st.markdown(
        "<div class='fs-card'><h4>Try an example</h4>"
        "<p style='margin:0 0 0.5rem 0;'>Click a sample article to load it into the text box.</p></div>",
        unsafe_allow_html=True,
    )
    example_cols = st.columns(len(EXAMPLES))
    for col, (label, text) in zip(example_cols, EXAMPLES.items()):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.article_text = text

    with st.form("article_form", clear_on_submit=False):
        article = st.text_area(
            "Paste a financial news article",
            value=st.session_state.article_text,
            height=320,
            placeholder=(
                "Paste the full text of a financial news article here, then "
                "click Analyze."
            ),
            key="article_text_area",
        )
        # Keep session state in sync with the live text area so re-clicking
        # an example after editing still loads the new sample.
        st.session_state.article_text = article
        submitted = st.form_submit_button("Analyze")

    if submitted:
        validation_error = _validate_article(article)
        if validation_error:
            st.session_state.analysis = None
            st.session_state.last_error = validation_error
        else:
            with st.spinner("Analyzing the article with Gemini..."):
                try:
                    raw = generate_analysis(
                        prompt=build_analysis_prompt(article),
                        system_instruction=SYSTEM_INSTRUCTION,
                    )
                    parsed = parse_analysis_response(raw)
                    st.session_state.analysis = parsed
                    st.session_state.last_error = None
                except GeminiConfigError as exc:
                    st.session_state.analysis = None
                    st.session_state.last_error = str(exc)
                except GeminiAPIError as exc:
                    st.session_state.analysis = None
                    st.session_state.last_error = str(exc)
                except ResponseParseError as exc:
                    st.session_state.analysis = None
                    st.session_state.last_error = (
                        "The model response could not be parsed: " + str(exc)
                    )

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if st.session_state.analysis:
        st.divider()
        st.markdown(
            "<h3 style='color:#f3f6fb !important;'>Results dashboard</h3>",
            unsafe_allow_html=True,
        )
        _render_results(st.session_state.analysis)
        st.markdown(f"<div class='fs-strip'>⚠️ {DISCLAIMER}</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='fs-footer'>FinSight AI · Generative AI Internship Project · "
        "Supported by Google for Developers</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()