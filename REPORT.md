# FinSight AI — Internship Project Report

**Generative AI-Powered Financial News Summarizer & Sentiment Insight Assistant**

---

## 1. Introduction

FinSight AI is a single-page web application that uses Generative AI to read
a financial news article a user pastes into the app and to produce a clear,
beginner-friendly analysis: a summary, a sentiment verdict with reasoning,
plain-English explanations of any financial jargon, and a short list of
positives and risks. The application is built strictly around the
Generative AI skill set covered during the internship — prompting
fundamentals, generative AI concepts, Gemini API usage, and responsible AI
grounding — and applies that skill set to a real business problem in the
finance domain.

The project is deliberately scoped as a single-workflow MVP so it can be
fully understood, built, tested, and demoed within an internship review
timeline.

## 2. Internship and Organisation Details

- **Intern:** Karri Shahanth Krishna Reddy
- **Institution:** Aditya University (Aditya Engineering College)
- **Program:** Virtual Internship – 2026, conducted by L4G
- **Domain:** Generative AI
- **Duration:** 10 weeks (May – July)
- **Mode:** Virtual
- **Achievement:** 22 Skill Badges
- **Supported by:** Google for Developers

The internship was a Google-supported Generative AI skills path. The badge
count and the "Google for Developers" support point to competencies in
prompting fundamentals, generative AI concepts, Gemini API usage, and
responsible AI. FinSight AI applies those competencies to the finance
domain.

## 3. Domain Background

Retail investors and finance/commerce students read financial news
constantly. That news is dense, long, and full of jargon such as P/E
ratio, EBITDA, free cash flow, and guidance. Even when a reader has the
time, judging whether an article is positive or negative for a company is
subjective, and explaining *why* it is bullish or bearish is harder still.
Most free tools show only the headline; they do not reason about tone or
unpack the jargon for a beginner.

## 4. Problem Statement

- Financial news is dense, long, and full of jargon.
- Judging whether an article is positive or negative is slow and subjective.
- Beginners cannot easily tell *why* an article is bullish or bearish.
- No lightweight, free tool turns a pasted news article into a clear
  summary + sentiment + plain-English explanation in one step.

## 5. Objectives

- **O1:** Automatically summarise a financial news article using GenAI.
- **O2:** Generate a sentiment verdict with text-grounded reasoning
  (no fabricated claims).
- **O3:** Simplify financial jargon into plain English.
- **O4:** Extract a short, structured "key takeaways" list from the article.
- **O5:** Demonstrate applied, responsible Generative AI use
  (grounded generation, no hallucinated financial claims).

## 6. Proposed Methodology

The project follows a standard, professional development lifecycle:

| Phase | Activities |
|---|---|
| 1. Requirement Analysis | Define the problem, target users, and MVP scope (summary, sentiment, jargon, takeaways, disclaimer only). |
| 2. System Design | Design the single-pipeline architecture, module breakdown, and the structured prompt/response format. |
| 3. UI Development | Build the Streamlit input page and the results dashboard layout (tabs, disclaimer banner). |
| 4. Gemini API Integration | Set up the Gemini API client, environment-variable-based key management, and error/timeout handling. |
| 5. Prompt Engineering | Design and iterate on the single structured prompt so Gemini reliably returns summary, sentiment + reasoning, jargon, and takeaways in a fixed, parseable format. |
| 6. Testing | Run the pipeline on sample articles of varying tone and length; verify parsing, sentiment grounding, and UI display. |
| 7. Bug Fixing | Resolve issues — malformed API responses, edge cases, and UI display issues. |
| 8. Documentation | Write the README, prepare the PPT, and finalise the report. |

## 7. System Architecture

```
        ┌───────────────────────┐
        │          User          │
        └───────────┬────────────┘
                     │ pastes financial news article
                     ▼
        ┌───────────────────────┐
        │   Streamlit Web App    │
        │   (Input Interface)    │
        └───────────┬────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Input Processing &         │
        │ Prompt Engineering Layer   │
        │ (builds a structured       │
        │  instruction prompt)       │
        └───────────┬────────────────┘
                     │ structured prompt
                     ▼
        ┌───────────────────────┐
        │   Google Gemini API    │
        │        (GenAI)         │
        └───────────┬────────────┘
                     │ raw AI response
                     ▼
        ┌────────────────────────────┐
        │ Structured Response Parser │
        └───────────┬────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │      Results Dashboard     │
        │ (Summary · Sentiment ·     │
        │  Jargon · Key Takeaways ·  │
        │  Disclaimer)               │
        └────────────────────────────┘
```

The architecture is intentionally a single linear pipeline — no branching
modules, no optional integrations, and no external data sources — so it
is easy to explain to a review panel and stable to demo live.

## 8. Module Description

1. **Input Handling Module** — A text area where the user pastes the
   article, plus an **Analyze** button. Empty / very-short input is
   rejected with a clear on-screen message.
2. **Prompt Engineering Layer** — A single, well-tested prompt template
   that asks Gemini for a structured response covering summary,
   sentiment, jargon, and takeaways in one call. A separate system
   instruction enforces the text-only grounding rule.
3. **GenAI Integration Module** — Reads the API key from the environment
   (never hard-coded), builds the `GenerativeModel`, sends the request,
   and converts failures into a clear, catchable error.
4. **Structured Response Parser** — Converts the model's strict JSON
   output into clean data for the UI. Tolerant of markdown fences and
   stray prose around the JSON object.
5. **Results Dashboard (UI / Presentation Layer)** — Streamlit tabs for
   Summary, Sentiment, Jargon, and Key Takeaways, plus a persistent
   disclaimer banner on the input page and again on the results page.

## 9. Technology Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit (Python) |
| Backend logic | Python |
| GenAI | Google Gemini API (`google-generativeai` SDK) |
| Environment / config | `python-dotenv` |

No database, no external market-data library, and no authentication layer
are part of the technology stack — this keeps the dependency list minimal
and the app fully self-contained.

## 10. Implementation Details

### 10.1 Project structure

```
finsight-ai/
├── app.py
├── requirements.txt
├── .env.example
├── modules/
│   ├── __init__.py
│   ├── prompt_templates.py
│   ├── genai_client.py
│   └── output_parser.py
├── tests/
│   ├── __init__.py
│   └── test_output_parser.py
├── assets/
│   ├── FinSight_AI_Review.pptx
│   └── screenshots/
├── generate_ppt.py
├── REPORT.md
├── PRESENTATION_SCRIPT.md
└── README.md
```

### 10.2 The structured prompt

The model is asked to respond with a strict JSON object containing:

```json
{
  "summary": "...",
  "sentiment": "Bullish | Bearish | Neutral",
  "reasoning": "...",
  "jargon":  [{"term": "...", "explanation": "..."}],
  "takeaways": {"positives": ["..."], "risks": ["..."]}
}
```

Rules baked into the prompt:

- Base every claim strictly on the article text provided.
- Do not use outside market knowledge.
- Do not give any buy / sell / hold recommendation.
- Return valid JSON, even if the article is empty or too short.

### 10.3 The UI

- A text area accepts the article.
- An **Analyze** button submits the form.
- Results are rendered in four tabs: **Summary · Sentiment · Jargon
  Explained · Key Takeaways**.
- A persistent **disclaimer banner** states the tool is educational and
  not financial advice.

### 10.4 Input validation and error handling

- Empty / very-short input is rejected with an on-screen message.
- Missing API key → `GeminiConfigError` → friendly on-screen error.
- API call failure → `GeminiAPIError` → friendly on-screen error.
- Unparseable response → `ResponseParseError` → friendly on-screen
  error.

## 11. Testing

| Test type | What it verifies |
|---|---|
| Unit | The parser maps the strict JSON response into `{summary, sentiment, reasoning, jargon[], takeaways{positives, risks}}`, tolerates markdown fences, normalises unknown sentiments to `Neutral`, drops malformed jargon entries, and rejects empty / non-JSON input. |
| Functional | Run the pipeline on 3–4 sample articles of mixed positive / negative / neutral tone and verify the sentiment reasoning is grounded in the article text. |
| Edge cases | Empty input, very short input, API timeout or error response. |
| UI | Tab display and persistent disclaimer visibility. |

Test command:

```bash
python -m unittest discover -s tests -t .
```

## 12. Results

- The Streamlit application runs locally with a single command:
  `streamlit run app.py`.
- The pipeline returns a concise summary, a sentiment verdict with
  text-grounded reasoning, a jargon glossary specific to the article,
  and a key-takeaways list (positives and risks) — all rendered on the
  results dashboard.
- A persistent disclaimer makes the educational scope of the tool
  clear at all times.
- No external data, no database, no authentication — the demo is stable
  and reproducible.

## 13. Limitations

- Requires an internet connection and Gemini API availability.
- Sentiment is based only on the text the user pastes — it is not a
  market prediction and does not use any live or external market data.
- No multi-user accounts, authentication, or persistent history — out
  of scope for a demo project.
- Not intended, and explicitly not positioned, as real financial or
  investment advice.

## 14. Future Scope

The following items are explicitly out of scope for this MVP and are
listed only to show awareness of a realistic growth path:

- Multi-article comparison (aggregate sentiment across several news sources).
- Optional live stock-price context alongside the analysis.
- A history / database layer to save past analyses.
- User accounts and multi-user support.
- Multi-language support.

## 15. Conclusion

FinSight AI is a focused MVP that applies Generative AI to a real,
relatable problem: helping beginners read financial news faster and
more confidently. A single linear pipeline — paste article → structured
prompt → Gemini → parsed results — keeps the architecture simple, the
demo stable, and the code easy to explain. Strict responsible-AI
grounding (text-only reasoning, no buy/sell claims, persistent
disclaimer) keeps the tool honest about being an educational
text-analysis aid, not a market predictor. The modular code (input,
prompt, GenAI client, parser, UI) makes future extension
straightforward.

## 16. References

- Google AI Studio — Gemini API documentation.
- Streamlit documentation — https://docs.streamlit.io/
- `google-generativeai` Python SDK — official Google Generative AI client.
- Approved internal PRD: *FinSight AI — Generative AI-Powered Financial
  News Summarizer & Sentiment Insight Assistant* (internship record).
