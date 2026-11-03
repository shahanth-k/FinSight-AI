"""Generate FinSight_AI_Review.pptx using python-pptx.

Content is taken directly from the approved FinSight_AI_PRD (1).md. No
external or invented features are introduced. ~10-minute review deck.
"""

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor


OUTPUT_PATH = Path("D:/tmroo/finsight-ai/assets/FinSight_AI_Review.pptx")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# ---------------- helpers ----------------

PRIMARY = RGBColor(0x1F, 0x3A, 0x68)      # deep navy
ACCENT = RGBColor(0x2E, 0x86, 0xC1)       # blue
TEXT = RGBColor(0x20, 0x20, 0x20)
SUBTLE = RGBColor(0x6B, 0x6B, 0x6B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BAND = RGBColor(0xEC, 0xF2, 0xFA)


def add_title_bar(slide, prs, title, subtitle=None):
    left = Inches(0)
    top = Inches(0)
    width = prs.slide_width
    height = Inches(0.9)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    bar.line.fill.background()
    bar.fill.solid()
    bar.fill.fore_color.rgb = PRIMARY
    tf = bar.text_frame
    tf.margin_left = Inches(0.4)
    tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = WHITE
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(13)
        p2.font.color.rgb = WHITE


def add_bullets(slide, bullets, left=Inches(0.5), top=Inches(1.1),
                width=Inches(9.0), height=Inches(5.5), size=18):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(size)
        p.font.color.rgb = TEXT
        p.space_after = Pt(6)


def add_two_columns(slide, left_title, left_bullets, right_title, right_bullets,
                    left=Inches(0.5), top=Inches(1.1), width=Inches(9.0),
                    height=Inches(5.5), size=16):
    half = Inches((9.0) / 2 - 0.1)
    # Left
    l = slide.shapes.add_textbox(left, top, half, height)
    ltf = l.text_frame
    ltf.word_wrap = True
    p = ltf.paragraphs[0]
    p.text = left_title
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT
    for item in left_bullets:
        p2 = ltf.add_paragraph()
        p2.text = f"• {item}"
        p2.font.size = Pt(size)
        p2.font.color.rgb = TEXT
        p2.space_after = Pt(4)
    # Right
    r = slide.shapes.add_textbox(Inches(0.5) + half + Inches(0.2), top, half, height)
    rtf = r.text_frame
    rtf.word_wrap = True
    p = rtf.paragraphs[0]
    p.text = right_title
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT
    for item in right_bullets:
        p2 = rtf.add_paragraph()
        p2.text = f"• {item}"
        p2.font.size = Pt(size)
        p2.font.color.rgb = TEXT
        p2.space_after = Pt(4)


def add_centered(slide, lines, size=20, color=TEXT, bold=False, top=Inches(2.0)):
    box = slide.shapes.add_textbox(Inches(0.5), top, Inches(9.0), Inches(4.0))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.font.bold = bold
        p.alignment = 1  # center


# ---------------- deck content ----------------

slides_content = [
    {
        "kind": "title",
        "title": "FinSight AI",
        "subtitle": "Generative AI-Powered Financial News Summarizer & Sentiment Insight Assistant",
        "meta": [
            "Intern: Karri Shahanth Krishna Reddy",
            "Institution: Aditya University (Aditya Engineering College)",
            "Program: Virtual Internship – 2026, conducted by L4G",
            "Domain: Generative AI · 10 weeks (May – July) · Mode: Virtual",
            "Achievement: 22 Skill Badges · Supported by Google for Developers",
        ],
    },
    {
        "kind": "bullets",
        "title": "Agenda",
        "bullets": [
            "Problem statement and motivation",
            "Proposed solution and objectives",
            "System architecture and module breakdown",
            "Technology stack",
            "Prompt engineering and responsible-AI grounding",
            "Implementation, UI, and testing",
            "Results, limitations, future scope, and conclusion",
        ],
    },
    {
        "kind": "bullets",
        "title": "Problem Statement",
        "bullets": [
            "Retail investors and finance students are flooded with financial news every day.",
            "Articles are dense, long, and full of jargon (P/E, EBITDA, guidance…).",
            "Judging whether an article is positive or negative is slow and subjective.",
            "Beginners cannot easily tell WHY an article is bullish or bearish.",
            "No lightweight free tool turns a pasted article into summary + sentiment + plain-English in one step.",
        ],
    },
    {
        "kind": "bullets",
        "title": "Proposed Solution",
        "bullets": [
            "Single-page web app: paste a financial news article, click Analyze.",
            "Google Gemini API produces, in one structured call:",
            "1. Concise summary of the article",
            "2. Sentiment verdict — Bullish / Bearish / Neutral — with text-grounded reasoning",
            "3. Plain-English explanation of financial jargon used in the article",
            "4. Key takeaways — positives and risks mentioned in the article",
            "Visible disclaimer: educational use only, NOT financial advice.",
            "No live data, no external feeds, no database — purely text-in, insight-out.",
        ],
    },
    {
        "kind": "two",
        "title": "Objectives",
        "left_title": "Functional Objectives",
        "left": [
            "O1: Summarise a financial news article using GenAI.",
            "O2: Sentiment verdict with text-grounded reasoning (no fabrication).",
            "O3: Simplify financial jargon into plain English.",
            "O4: Extract a short, structured key-takeaways list.",
            "O5: Demonstrate applied, responsible Generative AI use.",
        ],
        "right_title": "Non-Functional Objectives",
        "right": [
            "Usability: single page, no login, runs as soon as the app opens.",
            "Performance: typical response under ~15 seconds (API-bound).",
            "Reliability: graceful handling of empty input and API errors.",
            "Security: Gemini API key in environment variable, never hard-coded.",
            "Portability: Python + minimal free dependencies, zero infra cost.",
        ],
    },
    {
        "kind": "two",
        "title": "System Architecture",
        "left_title": "Pipeline (single linear flow)",
        "left": [
            "User pastes a financial news article",
            "Streamlit web app — input interface",
            "Input processing & prompt engineering layer",
            "Google Gemini API (GenAI)",
            "Structured response parser",
            "Results dashboard (Summary · Sentiment · Jargon · Takeaways)",
            "Persistent disclaimer banner",
        ],
        "right_title": "Why this architecture",
        "right": [
            "Single linear pipeline — no branching, no optional integrations.",
            "Easy to explain to a review panel.",
            "Stable to demo live — no dependency on external data sources.",
            "Stateless — no database, no auth, no persistence between sessions.",
        ],
    },
    {
        "kind": "bullets",
        "title": "Module-Wise Breakdown",
        "bullets": [
            "Input Handling Module — text area + Analyze button.",
            "Prompt Engineering Layer — single, well-tested structured prompt template.",
            "GenAI Integration Module — Gemini API call, basic error handling.",
            "Structured Response Parser — converts JSON output into clean data for the UI.",
            "Results Dashboard (UI / Presentation Layer) — tabs for each output type, persistent disclaimer.",
        ],
    },
    {
        "kind": "two",
        "title": "Technology Stack",
        "left_title": "Layers",
        "left": [
            "Frontend / UI: Streamlit (Python)",
            "Backend logic: Python",
            "GenAI: Google Gemini API (google-generativeai SDK)",
            "Environment / config: python-dotenv",
        ],
        "right_title": "Deliberate non-choices",
        "right": [
            "No database — app is stateless per analysis.",
            "No authentication — single-user demo scope.",
            "No live market data / no yfinance — out of scope.",
            "No external news fetcher — user pastes the article.",
            "Keeps dependency list minimal and the app fully self-contained.",
        ],
    },
    {
        "kind": "bullets",
        "title": "Prompt Engineering & Responsible AI",
        "bullets": [
            "Single instruction-based prompt requesting a fixed JSON output schema.",
            "Fields: summary, sentiment, reasoning, jargon[], takeaways{positives, risks}.",
            "Model is explicitly told to base EVERY claim on the supplied article text only.",
            "No use of outside market knowledge — prevents hallucinated financial facts.",
            "Model is told NEVER to give a buy / sell / hold recommendation.",
            "Output is strict JSON so the response is reliably parseable downstream.",
        ],
    },
    {
        "kind": "bullets",
        "title": "Implementation Highlights",
        "bullets": [
            "app.py — Streamlit page, form input, results dashboard with 4 tabs.",
            "modules/prompt_templates.py — system instruction + build_analysis_prompt().",
            "modules/genai_client.py — env-driven API key, model name, generate_analysis().",
            "modules/output_parser.py — strict JSON parse with tolerant fallback.",
            "Persistent disclaimer banner on the input page and again on results.",
            "Input validation: empty / too-short article → clear on-screen error.",
            "API failures surface as readable errors — no silent crashes.",
        ],
    },
    {
        "kind": "two",
        "title": "User Workflow & Demo Scenario",
        "left_title": "User workflow",
        "left": [
            "1. User opens the app.",
            "2. Pastes a financial news article.",
            "3. Clicks Analyze.",
            "4. App builds a structured prompt and calls Gemini.",
            "5. Gemini returns summary + sentiment + jargon + takeaways.",
            "6. Dashboard renders results, disclaimer remains visible.",
        ],
        "right_title": "Demo scenario (review)",
        "right": [
            "Paste a short realistic financial news article.",
            "Click Analyze — show the AI-generated summary.",
            "Show sentiment + reasoning tied to the article text.",
            "Show the jargon glossary for that specific article.",
            "Show the key takeaways (positives and risks).",
            "Point out the persistent disclaimer banner.",
        ],
    },
    {
        "kind": "bullets",
        "title": "Testing",
        "bullets": [
            "Unit tests: structured JSON response is parsed into summary, sentiment, jargon, takeaways.",
            "Functional tests: run on 3–4 sample articles of mixed positive / negative / neutral tone.",
            "Edge cases: empty input, very short input, API timeout / error response.",
            "UI tests: tab display, persistent disclaimer visibility.",
        ],
    },
    {
        "kind": "two",
        "title": "Results & Internship Alignment",
        "left_title": "What the project demonstrates",
        "left": [
            "Applied Generative AI: summarisation, sentiment reasoning, simplification.",
            "Prompt engineering: fixed JSON schema, single-call structured output.",
            "Responsible AI: text-grounded reasoning, no buy/sell claims, disclaimer.",
            "Clean modular Python code, stateless, demo-stable.",
        ],
        "right_title": "Internship alignment",
        "right": [
            "Intern: Karri Shahanth Krishna Reddy.",
            "Institution: Aditya University (Aditya Engineering College).",
            "Program: Virtual Internship – 2026, conducted by L4G.",
            "Domain: Generative AI · 10 weeks (May – July) · Virtual.",
            "Achievement: 22 Skill Badges · Supported by Google for Developers.",
        ],
    },
    {
        "kind": "two",
        "title": "Limitations & Future Scope",
        "left_title": "Limitations (honest)",
        "left": [
            "Requires internet and Gemini API availability.",
            "Sentiment is bound to the text the user pastes — not a market prediction.",
            "No multi-user accounts, auth, or persistent history — out of scope.",
            "Explicitly not positioned as real financial or investment advice.",
        ],
        "right_title": "Future scope (out of MVP)",
        "right": [
            "Multi-article comparison across several sources.",
            "Optional live stock-price context (deliberately excluded here).",
            "History / database layer to save past analyses.",
            "User accounts and multi-user support.",
            "Multi-language support.",
        ],
    },
    {
        "kind": "bullets",
        "title": "Conclusion",
        "bullets": [
            "FinSight AI is a focused MVP that applies Generative AI to a real, relatable problem.",
            "A single linear pipeline: paste article → structured prompt → Gemini → parsed results.",
            "Strict responsible-AI grounding: text-only reasoning, no buy/sell claims, persistent disclaimer.",
            "Modular code (input, prompt, GenAI client, parser, UI) makes future extension straightforward.",
            "The project directly applies the GenAI badge-track competencies — prompting, GenAI concepts, and responsible AI.",
        ],
    },
    {
        "kind": "thanks",
        "title": "Thank You",
    },
]


# ---------------- build ----------------

prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]


for item in slides_content:
    slide = prs.slides.add_slide(blank_layout)
    kind = item["kind"]
    title = item["title"]

    if kind == "title":
        add_title_bar(slide, prs, title)
        add_centered(
            slide,
            [item["subtitle"]] + item["meta"],
            size=16,
            color=TEXT,
            top=Inches(1.4),
        )
    elif kind == "thanks":
        add_title_bar(slide, prs, title)
        add_centered(
            slide,
            [
                "FinSight AI",
                "Generative AI-Powered Financial News Summarizer & Sentiment Insight Assistant",
                "",
                "Intern: Karri Shahanth Krishna Reddy · Aditya University",
                "Generative AI Internship – 2026, conducted by L4G",
            ],
            size=18,
            color=TEXT,
            top=Inches(2.2),
        )
    elif kind == "bullets":
        add_title_bar(slide, prs, title)
        add_bullets(slide, item["bullets"])
    elif kind == "two":
        add_title_bar(slide, prs, title)
        add_two_columns(
            slide,
            item["left_title"],
            item["left"],
            item["right_title"],
            item["right"],
        )

    # footer
    foot = slide.shapes.add_textbox(
        Inches(0.4), Inches(7.05), Inches(9.2), Inches(0.35)
    )
    fp = foot.text_frame.paragraphs[0]
    fp.text = (
        "FinSight AI · Generative AI Internship Project · "
        "Supported by Google for Developers"
    )
    fp.font.size = Pt(10)
    fp.font.color.rgb = SUBTLE


prs.save(str(OUTPUT_PATH))
print(f"Wrote: {OUTPUT_PATH}")
