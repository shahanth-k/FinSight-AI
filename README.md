# ⚡ FinSight AI — Stock Intelligence & Probability Analysis System

> **Advanced Generative AI-powered Stock Intelligence Platform**  
> Hybrid architecture: Deterministic technical analysis + Google Gemini AI synthesis

---

## 🚀 What Does It Do?

FinSight AI solves the problem of **fragmented investment analysis**. Instead of manually checking multiple platforms for charts, indicators, news, and sentiment — FinSight AI brings everything into one intelligent system:

1. **Enters** a company name or stock ticker
2. **Fetches** historical market data via yfinance (free, no API key needed)
3. **Calculates** RSI, MACD, Bollinger Bands, SMA 20/50/200, ATR, Momentum, Volume
4. **Analyzes** recent news sentiment and categorizes themes
5. **Fuses** signals using a transparent weighted-scoring methodology
6. **Synthesizes** a complete intelligence report using Google Gemini AI
7. **Presents** everything on a premium probability-based dashboard

---

## 📊 Dashboard Features

| Feature | Description |
|---------|-------------|
| **Market Outlook** | Strong Bullish / Moderately Bullish / Neutral / Moderately Bearish / High Risk |
| **Upside Probability** | Animated gauge showing estimated upside probability % |
| **Downside Probability** | Corresponding downside risk % |
| **Bullish Scenario** | Estimated upside price range (1-3 month horizon) |
| **Bearish Scenario** | Estimated downside price range (1-3 month horizon) |
| **Technical Signals** | Grid of all calculated indicators with Bullish/Bearish/Neutral badges |
| **Price Chart** | 90-day price with SMA 20, SMA 50, Bollinger Bands |
| **RSI Chart** | 14-period RSI with overbought/oversold zones |
| **MACD Chart** | MACD, Signal line, and histogram |
| **AI Intelligence Report** | Gemini-synthesized executive summary + narrative |
| **News Intelligence** | Sentiment analysis of 30-day news with categorized themes |
| **Explainable AI** | Full score breakdown table showing exactly how probability was derived |
| **Risk Factors** | Identified risk signals from technical + news data |
| **Positive Catalysts** | Identified bullish evidence |

---

## 🏗️ System Architecture

```
User Input (ticker/company name)
        │
        ▼
┌─────────────────────────────────────┐
│      Technical Analysis Engine       │  ← Deterministic Math
│  SMA, EMA, RSI, MACD, BB, ATR,      │
│  Momentum, Volume, Support/Resistance│
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      News Intelligence Engine        │  ← Keyword Sentiment
│  NewsAPI → Sentiment Scoring →       │
│  Theme Extraction → Signal           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Signal Fusion + Probability        │  ← Transparent Scoring
│  Technical Score (70%) +             │
│  News Score (30%) →                  │
│  Combined Score → Probability         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Gemini AI Synthesizer           │  ← AI Narrative
│  Explains the quantitative findings  │
│  in professional natural language    │
└──────────────┬──────────────────────┘
               │
        Premium Dashboard
```

---

## 🧮 Probability Methodology (Transparent)

```
1. Each technical indicator → Score [-1.0, +1.0]
2. Weighted average of all indicator scores → Technical Score
3. News keyword sentiment → News Score [-1.0, +1.0]
4. Combined = (Technical × 0.70) + (News × 0.30)
5. Volatility Drag = penalize for high annualized volatility
6. Final Score → Linear map to Probability:
   Score = -1.0 → 20% upside
   Score =  0.0 → 50% upside
   Score = +1.0 → 80% upside
7. High volatility pulls probability toward 50% (more uncertainty)
```

> **⚠️ DISCLAIMER**: These probabilities are analytical estimates from historical patterns — NOT guaranteed predictions or financial advice.

---

## 🛠️ Quick Setup

### Prerequisites
- Python 3.9+
- Internet connection (for yfinance and NewsAPI)

### Step 1: Clone / Download the project

### Step 2: Set up API Keys

```bash
copy .env.example .env
```

Edit `.env`:
```
GEMINI_API_KEY=your_key   # https://aistudio.google.com/app/apikey
NEWS_API_KEY=your_key     # https://newsapi.org/register (free)
```

> **Note**: Both API keys are optional. The system works without them:
> - Without Gemini Key → Uses intelligent rule-based synthesis
> - Without NewsAPI Key → Technical analysis only (no news section)

### Step 3: One-click Start (Windows)

```bash
start.bat
```

Or manually:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
python app.py
```

### Step 4: Open Browser

```
http://127.0.0.1:5000
```

---

## 🔑 API Keys (Free Tiers Available)

| Service | Purpose | Cost | Link |
|---------|---------|------|------|
| **Google Gemini** | AI synthesis & narrative generation | Free tier available | [Get Key](https://aistudio.google.com/app/apikey) |
| **NewsAPI** | Recent news fetching (30 days) | Free: 100 req/day | [Get Key](https://newsapi.org/register) |
| **yfinance** | Historical market data | **Free, no key needed** | Automatic |

---

## 📁 Project Structure

```
finsight-ai/
├── backend/
│   ├── app.py                  # Flask server + API routes
│   ├── technical_analysis.py   # RSI, MACD, SMA, ATR, signals
│   ├── news_intelligence.py    # NewsAPI + sentiment scoring
│   ├── signal_fusion.py        # Probability engine + scoring
│   ├── gemini_synthesizer.py   # Gemini AI integration + fallback
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Premium dashboard UI
│   ├── style.css               # Dark glassmorphism design
│   └── app.js                  # Charts + dynamic rendering
├── .env.example                # API key template
├── start.bat                   # One-click startup (Windows)
└── README.md
```

---

## 🎯 Supported Stocks

**US Markets**: AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN, META, NFLX, AMD, INTC, JPM, V, MSFT, and thousands more

**Indian Markets (NSE)**: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, WIPRO.NS, BAJFINANCE.NS, ITC.NS, and more

**Any yfinance-supported ticker**: Stocks, ETFs, Crypto (BTC-USD, ETH-USD), Indices (^NSEI, ^GSPC)

---

## ⚠️ Disclaimer

This system provides **educational analytical tools only**. All probability estimates are based on historical patterns and mathematical models:

- Not financial advice
- Not guaranteed predictions  
- Past performance ≠ future results
- Always consult a qualified financial advisor

---

*Built for educational and internship demonstration purposes.*  
*Stack: Python, Flask, yfinance, Google Gemini AI, Chart.js, Vanilla CSS*
