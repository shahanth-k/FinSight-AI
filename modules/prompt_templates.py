"""Prompt templates for the FinSight AI pipeline.

The single, well-tested prompt asks Gemini to return a strict JSON object
containing summary, sentiment, reasoning, jargon, and takeaways — grounded
ONLY in the user-provided article text.
"""

SYSTEM_INSTRUCTION = (
    "You are FinSight AI, an educational text-analysis assistant for financial "
    "news articles. You NEVER give financial or investment advice. You only "
    "summarize and explain content that is already present in the article the "
    "user provides. You must not rely on outside knowledge of any company, "
    "market, or ticker. If a piece of information is not stated in the article, "
    "do not invent it."
)


def build_analysis_prompt(article_text: str) -> str:
    """Build the single structured instruction prompt.

    The model is asked to respond with strict JSON so the response is reliably
    parseable downstream.
    """
    article = article_text.strip()
    return (
        "Analyze the following financial news article and respond ONLY with a "
        "single valid JSON object — no prose, no markdown fences.\n\n"
        "Required JSON schema:\n"
        "{\n"
        '  "summary": string,   // 2-4 sentence concise summary of the article\n'
        '  "sentiment": "Bullish" | "Bearish" | "Neutral",\n'
        '  "reasoning": string, // 2-4 sentences explaining WHY the sentiment '
        'verdict follows from the article text. Quote or paraphrase specific '
        'phrases from the article.\n'
        '  "jargon": [\n'
        '    {"term": string, "explanation": string} // each financial term '
        'used in the article, explained in plain English for a beginner\n'
        "  ],\n"
        '  "takeaways": {\n'
        '    "positives": [string], // short bullet-style positives from the article\n'
        '    "risks": [string]      // short bullet-style risks from the article\n'
        "  }\n"
        "}\n\n"
        "Rules:\n"
        "- Base EVERY claim strictly on the article text provided.\n"
        "- Do not use outside market knowledge.\n"
        "- Do not give any buy / sell / hold recommendation.\n"
        "- If the article is empty, nonsensical, or too short to analyze, still "
        'return valid JSON with empty lists/strings and sentiment "Neutral".\n\n'
        "ARTICLE:\n"
        f"{article}"
    )