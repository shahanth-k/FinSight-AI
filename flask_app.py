"""FinSight AI v2 — Flask Stock Intelligence Platform."""

from __future__ import annotations

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from modules.stock_data import fetch_stock_data, resolve_ticker, fmt_large
from modules.stock_analyzer import compute_stock_intelligence

load_dotenv()

app = Flask(__name__)

QUICK_PICKS = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "TCS.NS", "RELIANCE.NS"]
QUICK_LABELS = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "TCS", "RELIANCE"]


@app.route("/")
def index():
    return render_template("index.html",
                           quick_picks=list(zip(QUICK_PICKS, QUICK_LABELS)))


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    body = request.get_json(force=True) or {}
    query = (body.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Please enter a stock ticker or company name."}), 400

    ticker = resolve_ticker(query)
    stock = fetch_stock_data(ticker)

    if stock.get("error") and stock.get("price") is None:
        return jsonify({"error": f"Could not fetch data for '{ticker}'. Check the ticker and try again."}), 404

    intelligence = compute_stock_intelligence(stock)

    return jsonify({
        "stock": stock,
        "intelligence": intelligence,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
