"""
FinSight AI - Main Flask Application
Serves the frontend static files and provides the /api/analyze endpoint.
"""

import os
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from technical_analysis import TechnicalAnalysisEngine
from news_intelligence import NewsIntelligenceEngine
from signal_fusion import SignalFusionEngine
from gemini_synthesizer import GeminiSynthesizer

# ── Load environment variables ─────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# ── App setup ──────────────────────────────────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)


# ── Frontend Routes ────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ── API Routes ─────────────────────────────────────────────────────────────

@app.route('/api/analyze', methods=['POST'])
def analyze():
    body = request.get_json(silent=True) or {}
    query = (body.get('query') or '').strip()

    if not query:
        return jsonify({'success': False, 'error': 'Please enter a stock ticker or company name.'}), 400

    try:
        # 1. Technical Analysis (deterministic, no AI)
        ta_engine = TechnicalAnalysisEngine()
        technical = ta_engine.analyze(query)

        if technical.get('error'):
            return jsonify({'success': False, 'error': technical['error']}), 400

        # 2. News Intelligence
        news_engine = NewsIntelligenceEngine()
        news = news_engine.analyze(
            technical.get('company_name', query),
            technical.get('ticker', query)
        )

        # 3. Signal Fusion + Probability Engine
        fusion_engine = SignalFusionEngine()
        fusion = fusion_engine.calculate(technical, news)

        # 4. Gemini AI Synthesis
        synthesizer = GeminiSynthesizer()
        synthesis = synthesizer.synthesize(technical, news, fusion)

        return jsonify({
            'success': True,
            'ticker': technical['ticker'],
            'company_name': technical['company_name'],
            'technical': technical,
            'news': news,
            'fusion': fusion,
            'synthesis': synthesis,
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'online',
        'gemini': bool(os.getenv('GEMINI_API_KEY')),
        'news': bool(os.getenv('NEWS_API_KEY')),
    })


# ── Entry Point ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  FinSight AI -- Stock Intelligence System")
    print("="*60)
    print(f"  Frontend: http://127.0.0.1:5000")
    print(f"  API:      http://127.0.0.1:5000/api/analyze")
    print(f"  Gemini:   {'[OK] Configured' if os.getenv('GEMINI_API_KEY') else '[--] Not configured (rule-based fallback)'}")
    print(f"  News API: {'[OK] Configured' if os.getenv('NEWS_API_KEY') else '[--] Not configured (news disabled)'}")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, use_reloader=False)
