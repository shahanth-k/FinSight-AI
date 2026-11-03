# FinSight AI

**Generative AI-Powered Financial News Summarizer & Sentiment Insight Assistant**

A single-page Streamlit web app that uses the Google Gemini API to summarise
a pasted financial news article, classify its sentiment (Bullish / Bearish /
Neutral) with text-grounded reasoning, explain the financial jargon in plain
English, and extract a short list of positives and risks.

> Educational use only. FinSight AI does not provide financial, investment, or
> trading advice and does not use any live market data.

---

## Project Context

- **Intern:** Karri Shahanth Krishna Reddy
- **Institution:** Aditya University (Aditya Engineering College)
- **Program:** Virtual Internship – 2026, conducted by L4G
- **Domain:** Generative AI
- **Duration:** 10 weeks (May – July)
- **Mode:** Virtual
- **Achievement:** 22 Skill Badges
- **Supported by:** Google for Developers

---

## Features

- Paste any financial news article into a text area and click **Analyze**.
- AI-generated **summary** of the article.
- **Sentiment verdict** (Bullish / Bearish / Neutral) with reasoning grounded
  in the article text — not on outside market knowledge.
- **Jargon glossary** — every financial term in the article, explained in
  plain English.
- **Key takeaways** — short lists of positives and risks mentioned in the
  article.
- A persistent **disclaimer banner** makes the educational scope clear at
  all times.

## Tech Stack

- **Frontend / UI:** Streamlit (Python)
- **Backend:** Python
- **GenAI:** Google Gemini API (`google-generativeai` SDK)
- **Config:** `python-dotenv`

No database, no authentication, no live market data — by design, to keep
the dependency list minimal and the demo stable.

## Folder Structure

```
finsight-ai/
├── app.py
├── generate_ppt.py            # builds the review PPT from this README/PRD
├── requirements.txt
├── .env.example               # template for GEMINI_API_KEY
├── modules/
│   ├── __init__.py
│   ├── prompt_templates.py
│   ├── genai_client.py
│   └── output_parser.py
├── assets/
│   ├── FinSight_AI_Review.pptx
│   └── screenshots/
├── tests/
├── REPORT.md                  # internship project report
├── PRESENTATION_SCRIPT.md     # 10-minute review script
└── README.md
```

## Setup

1. **Clone or copy** this folder.
2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure the API key:**
   - Get a free Gemini API key from Google AI Studio.
   - Copy `.env.example` to `.env`:
     ```
     GEMINI_API_KEY=your_real_key_here
     GEMINI_MODEL=gemini-1.5-flash
     ```
   - The app reads the key from the environment at runtime; it is never
     hard-coded.

## Run

```bash
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

## Usage

1. Read the disclaimer banner.
2. Paste a financial news article into the text area.
3. Click **Analyze**.
4. Review the **Summary / Sentiment / Jargon / Key Takeaways** tabs.
5. Close the tab — nothing is stored.

## Architecture

```
User → Streamlit Input → Prompt Engineering Layer → Gemini API
                                                       │
                                                       ▼
                       Results Dashboard ← Structured Response Parser
```

A single, linear pipeline. No branching modules, no external data sources.
This keeps the demo reliable and the code easy to explain in a review.

## Testing

Manual and unit checks live in `tests/`. The core unit test verifies the
structured JSON response from Gemini is parsed into the canonical
`{summary, sentiment, reasoning, jargon[], takeaways{positives, risks}}`
shape.

## Limitations

- Requires internet and Gemini API availability.
- Sentiment reflects only the text the user pastes.
- No accounts, no history, no live market data — by design.
- Educational use only — **not** financial advice.

## License / Use

This is an internship project. Use the code as a learning reference.
