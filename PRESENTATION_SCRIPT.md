# FinSight AI — 10-Minute Review Script

> Use this as a practice script. Time markers are approximate. Speak
> slowly and pause on the demo step.

---

**[0:00 – 0:30] Title slide**

"Good morning / afternoon. I'm Karri Shahanth Krishna Reddy, from Aditya
University, Aditya Engineering College. This is my Generative AI
internship project for 2026, conducted by L4G — supported by Google for
Developers.

The project is called **FinSight AI** — a Generative AI-powered
financial news summarizer and sentiment insight assistant."

---

**[0:30 – 1:15] Problem statement**

"Every day, retail investors and finance students read financial news
articles that are long, dense, and full of jargon — P/E ratio, EBITDA,
guidance, and so on. Even when they have the time, judging whether an
article is positive or negative is subjective. And explaining *why* it
is bullish or bearish is harder still.

Most free tools just show a headline. They do not reason about tone or
unpack the jargon for a beginner. That is the gap this project targets."

---

**[1:15 – 2:15] Proposed solution**

"The solution is a single-page web app. The user pastes a financial news
article, clicks **Analyze**, and Google Gemini produces four things in
one structured call:

1. A concise summary of the article.
2. A sentiment verdict — Bullish, Bearish, or Neutral — with
   text-grounded reasoning.
3. A plain-English explanation of the financial jargon used.
4. A short key-takeaways list — positives and risks.

A persistent disclaimer on the page makes the educational scope clear
at all times. There is no live market data, no database, and no
authentication — every output is generated purely from the text the
user pastes in."

---

**[2:15 – 3:15] Objectives**

"Functionally, the project has five objectives: automatic summarisation,
sentiment with grounded reasoning, jargon simplification, structured
key-takeaways extraction, and an applied demonstration of responsible
Generative AI use.

Non-functionally, the app is single-page, requires no login, and runs
as soon as it opens. The API key is stored in an environment variable
and is never hard-coded. And the whole thing runs on Python with a
very small set of free dependencies — zero infrastructure cost."

---

**[3:15 – 4:15] Architecture**

"The architecture is a single, linear pipeline. The user pastes an
article into the Streamlit web app. The app builds a single structured
prompt and sends it to the Gemini API. Gemini returns a strict JSON
response. A parser converts that JSON into clean data for the UI, and
the results dashboard shows the four sections in tabs, with the
disclaimer visible throughout.

This is intentionally a single pipeline — no branching modules, no
optional integrations, no external data sources. It is easy to explain
to a review panel and stable to demo live."

---

**[4:15 – 5:00] Module breakdown**

"There are five modules:

1. **Input Handling** — text area and Analyze button.
2. **Prompt Engineering** — a single, well-tested prompt template.
3. **GenAI Integration** — Gemini API call, basic error handling.
4. **Structured Response Parser** — JSON to UI data.
5. **Results Dashboard** — tabs and persistent disclaimer."

---

**[5:00 – 5:45] Technology stack**

"The stack is intentionally minimal. Streamlit for the UI, Python for
the backend, the Google Gemini API through the `google-generativeai`
SDK, and `python-dotenv` for environment configuration.

There is no database, no authentication, and no external market-data
library. By design — to keep the dependency list small and the demo
reliable."

---

**[5:45 – 6:30] Prompt engineering & responsible AI**

"The most important part of the project is the prompt. It asks Gemini
to respond with a strict JSON object — summary, sentiment, reasoning,
jargon, and takeaways — and it explicitly restricts the model to
reasoning *only* from the article text provided. No outside market
knowledge. No buy, sell, or hold recommendations.

This is a responsible-AI grounding technique. It keeps the model
honest about being a text-analysis aid, not a market predictor."

---

**[6:30 – 7:30] Implementation highlights & demo**

"Let me show the working app. *[Demo]*

I paste a short financial news article into the text area, and I click
**Analyze**. Within a few seconds, the dashboard renders the four
sections in tabs. Here is the summary. Here is the sentiment verdict
with the reasoning — you can see the reasoning quotes and paraphrases
specific phrases from the article. Here is the jargon glossary, with
every financial term in *this* article explained in plain English. And
here are the key takeaways — positives on the left, risks on the right.

The disclaimer is visible on the input page and again on the results
page. Nothing is stored, logged, or persisted."

---

**[7:30 – 8:15] Testing**

"I tested the system at three levels. Unit tests verify that the
parser correctly turns Gemini's strict JSON output into the canonical
shape — summary, sentiment, reasoning, jargon, and takeaways — and
that it tolerates markdown fences and stray prose.

Functional tests run the pipeline on three to four sample articles of
mixed tone and verify that the sentiment reasoning is grounded in the
article text. And I tested edge cases: empty input, very short input,
and API errors — all of which surface as clear on-screen messages."

---

**[8:15 – 9:00] Internship alignment**

"This project maps directly onto the GenAI badge-track competencies I
covered during the internship — prompting fundamentals, generative AI
concepts, Gemini API usage, and responsible AI grounding. The
internship itself was a Google-supported Generative AI skills path,
ten weeks, virtual, and the certificate records twenty-two skill
badges."

---

**[9:00 – 9:30] Limitations and future scope**

"Honestly, the tool depends on Gemini API availability. Its sentiment
is bound to whatever the user pastes in. There are no accounts, no
history, and no live market data — by design, not by oversight.

Future enhancements — explicitly out of scope here — would include
multi-article comparison, optional live stock-price context, a history
layer, user accounts, and multi-language support. The modular design
makes those straightforward to add later."

---

**[9:30 – 10:00] Conclusion and thanks**

"To conclude: FinSight AI is a focused MVP that applies Generative AI
to a real, relatable problem — helping beginners read financial news
faster and more confidently. A single linear pipeline keeps the
architecture simple, the demo stable, and the code easy to explain.

Thank you. I'm happy to take questions."
