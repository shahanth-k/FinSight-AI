# FinSight AI — Review-Panel Q&A

> Answers are based strictly on the approved PRD and the actual
> implementation. No invented features.

---

### Q1. Why did you choose this project?
My internship was in Generative AI, and I wanted to apply it outside a
purely academic use case. Financial news analysis is a real, relatable
business problem where GenAI's summarisation and reasoning skills add
clear value — and the scope was small enough to finish and demo
properly within the timeline.

### Q2. Isn't this giving financial advice? Is that risky?
No. The tool only summarises and explains sentiment already present in
the article the user pastes. It never issues a buy, sell, or hold
recommendation, and a disclaimer is visible on the input page and
again on the results page stating that the tool is for educational
purposes only.

### Q3. Which GenAI model did you use, and why?
Google's Gemini API — through the official `google-generativeai` Python
SDK. It aligns with the certificate, since the internship was
Google-supported, and it has a free tier suitable for a student project
with zero infrastructure cost. The model name is configurable via the
`GEMINI_MODEL` environment variable; the default is `gemini-1.5-flash`.

### Q4. How do you prevent the AI from hallucinating market facts?
The prompt explicitly restricts the model to reasoning only from the
article text provided — not from any outside "knowledge" about the
company, the market, or the ticker. The system instruction repeats the
same rule. This is a responsible-AI grounding technique that keeps the
output tied to the input.

### Q5. What is the system architecture?
A single linear pipeline. The user pastes an article into the Streamlit
web app. The app builds one structured prompt and sends it to the
Gemini API. The API returns a strict JSON response covering summary,
sentiment, reasoning, jargon, and takeaways. A parser converts that
JSON into clean data for the UI, and the results dashboard shows the
four sections in tabs, with the disclaimer visible throughout.

### Q6. Why doesn't the app use live stock prices or a database?
The project intentionally focuses on one core skill — using GenAI to
analyse and explain text — rather than integrating multiple external
systems. Keeping it to a single, well-tested pipeline made the app
more reliable to build, test, and demo within the internship timeline.
A database and live data are explicitly listed under future scope.

### Q7. What was the most challenging part?
Prompt engineering — making sure the sentiment reasoning was
consistently grounded in the article text and returned in a structured
JSON format the app could reliably parse. I iterated on the prompt
several times to make the model return exactly the fields the parser
expects.

### Q8. How does this relate to the skill badges you earned?
It directly applies the badge-track areas: prompting fundamentals,
generative AI concepts, Gemini API usage, and responsible AI grounding.
The persistent disclaimer, the text-only reasoning rule, and the
single structured prompt are all concrete expressions of those
competencies.

### Q9. Is this scalable beyond a demo?
Yes. The modular design separates input handling, prompt engineering,
the GenAI client, the response parser, and the UI. Features like live
market data, a history layer, or user accounts can be added later
without restructuring the core pipeline. They were deliberately left
out of this MVP to keep it stable and demo-ready.

### Q10. What are its limitations?
It depends on Gemini API availability, its sentiment is bound entirely
by whatever the input article says, and it deliberately avoids any real
trading or investment-advice functionality. There is no
authentication, no persistent history, and no live market data — all
out of scope for this MVP.

### Q11. How is the API key handled?
The Gemini API key is read from the `GEMINI_API_KEY` environment
variable via `python-dotenv`. It is never hard-coded. The repository
ships a `.env.example` template, and a missing key surfaces as a clear
on-screen error.

### Q12. What happens if the model returns a malformed response?
The `output_parser` module tries several fallbacks — removing markdown
fences, extracting the first JSON object, coercing unknown sentiment
values to `Neutral` — and only raises a `ResponseParseError` if the
response truly cannot be parsed. The UI catches that error and shows a
clear message instead of crashing.

### Q13. Could this be used for live trading or real investment decisions?
No. The disclaimer explicitly says it is educational, not financial
advice. The model is also told in the prompt to never give a buy, sell,
or hold recommendation. The tool is a text-analysis aid, not a market
predictor.
