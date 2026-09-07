/**
 * FinSight AI — Frontend Application
 * Handles API calls, dynamic UI rendering, Chart.js visualizations,
 * animated probability gauges, and complete dashboard state management.
 */

'use strict';

// ── Configuration ──────────────────────────────────────────────────────────
const API_BASE = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
  ? 'http://127.0.0.1:5000'
  : '';

const API_ANALYZE = `${API_BASE}/api/analyze`;

// ── Chart.js Defaults ──────────────────────────────────────────────────────
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.07)';
Chart.defaults.font.family = "'Inter', system-ui, sans-serif";

// ── Chart Registry ─────────────────────────────────────────────────────────
const charts = { price: null, rsi: null, macd: null };

// ── App State ──────────────────────────────────────────────────────────────
let isLoading = false;

// ══ ENTRY POINT ═══════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  checkHealth();
});

function setupEventListeners() {
  const form  = document.getElementById('search-form');
  const input = document.getElementById('search-input');

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = input.value.trim();
    if (query) triggerAnalysis(query);
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const query = input.value.trim();
      if (query) triggerAnalysis(query);
    }
  });
}

function quickSearch(ticker) {
  document.getElementById('search-input').value = ticker;
  triggerAnalysis(ticker);
}

// ══ HEALTH CHECK ══════════════════════════════════════════════════════════
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`, { method: 'GET' });
    if (!res.ok) throw new Error();
    const data = await res.json();
    const badge = document.getElementById('status-badge');
    badge.textContent = `Live ${data.gemini ? '+ Gemini AI' : '| No Gemini Key'}`;
  } catch {
    const badge = document.getElementById('status-badge');
    badge.textContent = '⚠ Backend Offline';
    badge.style.color = '#ef4444';
    badge.style.borderColor = 'rgba(239,68,68,0.4)';
  }
}

// ══ MAIN ANALYSIS FLOW ════════════════════════════════════════════════════
async function triggerAnalysis(query) {
  if (isLoading) return;
  isLoading = true;

  showLoading();
  destroyAllCharts();

  let loadingStepInterval = animateLoadingSteps();

  try {
    const response = await fetch(API_ANALYZE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    const data = await response.json();

    clearInterval(loadingStepInterval);

    if (!response.ok || !data.success) {
      showError(data.error || 'Analysis failed. Please check the ticker and try again.');
      return;
    }

    renderDashboard(data);

  } catch (err) {
    clearInterval(loadingStepInterval);
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      showError('Cannot connect to FinSight AI backend. Make sure the Flask server is running on port 5000.\n\nRun: python backend/app.py');
    } else {
      showError(`Unexpected error: ${err.message}`);
    }
  } finally {
    isLoading = false;
    hideLoading();
  }
}

function animateLoadingSteps() {
  const steps = [
    'Fetching historical market data via yfinance...',
    'Calculating RSI, MACD, Bollinger Bands...',
    'Analyzing Moving Averages & Support/Resistance...',
    'Running Signal Fusion & Probability Engine...',
    'Fetching and analyzing recent news...',
    'Synthesizing findings with Google Gemini AI...',
    'Building your intelligence report...',
  ];
  let i = 0;
  const el = document.getElementById('loading-step');
  return setInterval(() => {
    if (el) el.textContent = steps[i % steps.length];
    i++;
  }, 1600);
}

// ══ STATE MANAGEMENT ══════════════════════════════════════════════════════
function showLoading() {
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('error-state').classList.add('hidden');
  document.getElementById('dashboard').classList.add('hidden');
  document.getElementById('loading-state').classList.remove('hidden');

  const btn = document.getElementById('analyze-btn');
  btn.disabled = true;
  document.getElementById('btn-icon').textContent = '⏳';
  document.getElementById('btn-text').textContent = 'Analyzing...';
}

function hideLoading() {
  document.getElementById('loading-state').classList.add('hidden');
  const btn = document.getElementById('analyze-btn');
  btn.disabled = false;
  document.getElementById('btn-icon').textContent = '⚡';
  document.getElementById('btn-text').textContent = 'Analyze';
}

function showError(message) {
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('dashboard').classList.add('hidden');
  document.getElementById('loading-state').classList.add('hidden');
  document.getElementById('error-state').classList.remove('hidden');
  document.getElementById('error-message').textContent = message;
}

function showDashboard() {
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('error-state').classList.add('hidden');
  document.getElementById('loading-state').classList.add('hidden');
  document.getElementById('dashboard').classList.remove('hidden');
}

// ══ DASHBOARD RENDERING ═══════════════════════════════════════════════════
function renderDashboard(data) {
  const { technical: ta, news, fusion, synthesis } = data;

  renderStockHeader(ta);
  renderOutlook(fusion, ta);
  renderProbabilityGauge(fusion);
  renderProbabilityBars(fusion);
  renderRiskReward(fusion);
  renderScenarios(fusion, ta);
  renderKPIBar(ta);
  renderSignalsGrid(ta.signals || []);
  renderSynthesis(synthesis);
  renderCatalystsAndRisks(synthesis);
  renderNews(news);
  renderXAI(synthesis, fusion);

  // Charts rendered after DOM is visible
  showDashboard();
  setTimeout(() => {
    renderPriceChart(ta.chart_data, ta.current_price);
    renderRSIChart(ta.chart_data);
    renderMACDChart(ta.chart_data);
  }, 100);

  // Scroll to dashboard
  document.getElementById('dashboard').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Stock Header ────────────────────────────────────────────────────────────
function renderStockHeader(ta) {
  const cur = ta.currency || 'USD';
  const sym = getCurrencySymbol(cur);

  setText('stock-ticker-badge', `📊 ${ta.ticker}`);
  setText('stock-name', ta.company_name);
  setText('stock-price', `${sym}${formatNum(ta.current_price)}`);

  setText('stock-sector', `📂 ${ta.sector || 'Unknown'}`);
  setText('stock-exchange', `🏛 ${ta.exchange || cur}`);
  setText('stock-cap', ta.market_cap ? `💰 ${formatMarketCap(ta.market_cap)}` : '');
  setText('stock-pe', ta.pe_ratio ? `📊 P/E: ${ta.pe_ratio.toFixed(1)}` : '📊 P/E: N/A');

  renderPriceChange('change-1d', ta.price_change_1d, '1D');
  renderPriceChange('change-5d', ta.price_change_5d, '5D');
  renderPriceChange('change-20d', ta.price_change_20d, '20D');
}

function renderPriceChange(id, val, label) {
  const el = document.getElementById(id);
  if (!el) return;
  if (val === null || val === undefined) { el.textContent = `${label} N/A`; return; }
  const sign = val >= 0 ? '+' : '';
  el.textContent = `${label} ${sign}${val.toFixed(2)}%`;
  el.className = `price-change ${val > 0 ? 'up' : val < 0 ? 'down' : 'flat'}`;
}

// ── Market Outlook ──────────────────────────────────────────────────────────
function renderOutlook(fusion, ta) {
  const outlook = fusion.market_outlook || 'Neutral';
  const score   = fusion.combined_score || 0;

  const badge = document.getElementById('outlook-badge');
  badge.textContent = outlook;
  badge.className = `outlook-badge ${outlookClass(outlook)}`;

  setText('outlook-score-line',
    `Combined Signal Score: ${score.toFixed(3)} | Technical: ${(fusion.technical_score||0).toFixed(3)} (70%) + News: ${(fusion.news_score||0).toFixed(3)} (30%)`
  );

  const noteMap = {
    'Strong Bullish':    '🟢 Multiple indicators are aligned bullishly. Strong momentum across technical and fundamental signals.',
    'Moderately Bullish':'🔵 More bullish signals than bearish. Conditions are favorable but not overwhelmingly so.',
    'Neutral':           '⚪ Technical signals are mixed with no clear directional bias. Await confirmation.',
    'Moderately Bearish':'🟡 More bearish signals than bullish. Caution is warranted; downside risk elevated.',
    'High Risk':         '🔴 Strong bearish signals and/or extreme volatility. High probability of continued downside.',
  };
  setText('outlook-note', noteMap[outlook] || 'Analysis complete.');
}

function outlookClass(outlook) {
  const map = {
    'Strong Bullish':    'strong-bullish',
    'Moderately Bullish':'mod-bullish',
    'Neutral':           'neutral',
    'Moderately Bearish':'mod-bearish',
    'High Risk':         'high-risk',
  };
  return map[outlook] || 'neutral';
}

// ── Probability Gauge ───────────────────────────────────────────────────────
function renderProbabilityGauge(fusion) {
  const upside = fusion.upside_probability || 50;
  const circle = document.getElementById('gauge-circle');
  const radius = 64;
  const circumference = 2 * Math.PI * radius; // 402.12

  // Determine color based on upside
  let color = '#94a3b8';
  if (upside >= 65) color = '#10b981';
  else if (upside >= 55) color = '#06b6d4';
  else if (upside <= 35) color = '#ef4444';
  else if (upside <= 45) color = '#f97316';

  circle.style.stroke = color;

  // Animate: offset from full (hidden) to partial fill
  const offset = circumference - (upside / 100) * circumference;

  // Start from empty then fill
  requestAnimationFrame(() => {
    circle.style.strokeDashoffset = circumference; // reset
    setTimeout(() => {
      circle.style.strokeDashoffset = offset;
    }, 200);
  });

  // Animated counter
  animateCounter('gauge-pct', 0, upside, 1200, (v) => `${Math.round(v)}%`);
  setText('gauge-label', `${fusion.market_outlook || 'Neutral'}`);
  setText('gauge-note', `${upside}% upside / ${fusion.downside_probability || 50}% downside probability`);

  const gaugeEl = document.getElementById('gauge-pct');
  if (gaugeEl) gaugeEl.style.color = color;
}

// ── Probability Bars ────────────────────────────────────────────────────────
function renderProbabilityBars(fusion) {
  const up   = fusion.upside_probability || 50;
  const down = fusion.downside_probability || 50;

  setText('upside-pct-val', `${up}%`);
  setText('downside-pct-val', `${down}%`);

  setTimeout(() => {
    setWidth('upside-bar',   `${up}%`);
    setWidth('downside-bar', `${down}%`);
  }, 300);
}

// ── Risk & Reward ───────────────────────────────────────────────────────────
function renderRiskReward(fusion) {
  const risk = fusion.risk_level || {};
  const conf = fusion.confidence  || {};

  // Risk Level
  const riskEl = document.getElementById('risk-level-val');
  if (riskEl) {
    riskEl.textContent = risk.level || '—';
    riskEl.style.color = risk.color || 'var(--text-primary)';
  }

  const factors = (risk.factors || []).slice(0, 2);
  setText('risk-factors-list', factors.join(' · ') || 'No major risk flags');

  // RR Ratio
  setText('rr-ratio-val', fusion.risk_reward_ratio || '—');

  // Confidence
  setText('confidence-val', `${conf.level || '—'} (${conf.pct || 0}%)`);
  setText('confidence-note', conf.note || '');
  setTimeout(() => setWidth('confidence-bar', `${conf.pct || 0}%`), 300);
}

// ── Scenarios ───────────────────────────────────────────────────────────────
function renderScenarios(fusion, ta) {
  const bull = fusion.bullish_scenario || {};
  const bear = fusion.bearish_scenario || {};
  const sym  = getCurrencySymbol(ta.currency);

  setText('bull-range', `+${bull.low_pct || '—'}% to +${bull.high_pct || '—'}%`);
  setText('bull-prices', `Target: ${sym}${bull.low_target || '—'} → ${sym}${bull.high_target || '—'}`);
  setText('bull-basis',  bull.basis || '');
  setText('bull-horizon', bull.horizon || '1–3 months');

  setText('bear-range', `-${bear.low_pct || '—'}% to -${bear.high_pct || '—'}%`);
  setText('bear-prices', `Target: ${sym}${bear.low_target || '—'} → ${sym}${bear.high_target || '—'}`);
  setText('bear-basis',  bear.basis || '');
  setText('bear-horizon', bear.horizon || '1–3 months');
}

// ── KPI Bar ─────────────────────────────────────────────────────────────────
function renderKPIBar(ta) {
  const sym = getCurrencySymbol(ta.currency);
  const dq  = ta.data_quality || {};

  setText('kpi-52h', ta.week_52_high ? `${sym}${formatNum(ta.week_52_high)}` : 'N/A');
  setText('kpi-52l', ta.week_52_low  ? `${sym}${formatNum(ta.week_52_low)}`  : 'N/A');
  setText('kpi-vol',  ta.volatility_annualized ? `${ta.volatility_annualized}%` : 'N/A');
  setText('kpi-atr',  ta.atr ? `${sym}${ta.atr}` : 'N/A');
  setText('kpi-atr-pct', ta.atr_pct ? `${ta.atr_pct}% of price` : 'Average true range');
  setText('kpi-volr', ta.volume_ratio ? `${ta.volume_ratio}x` : 'N/A');
  setText('kpi-dq',   dq.grade || 'N/A');
  setText('kpi-dq-sub', `${dq.records || 0} days history`);
}

// ── Technical Signals Grid ──────────────────────────────────────────────────
function renderSignalsGrid(signals) {
  const container = document.getElementById('signals-grid');
  if (!container) return;

  container.innerHTML = '';

  let bullish = 0, bearish = 0, neutral = 0;
  signals.forEach(sig => {
    if (sig.signal === 'Bullish') bullish++;
    else if (sig.signal === 'Bearish') bearish++;
    else neutral++;

    const card = document.createElement('div');
    card.className = 'signal-card';
    card.setAttribute('role', 'article');
    card.setAttribute('aria-label', `${sig.indicator}: ${sig.signal}`);
    card.innerHTML = `
      <div class="signal-top">
        <div class="signal-name">${esc(sig.indicator)}</div>
        <div class="signal-badge ${esc(sig.signal)}">${esc(sig.signal)}</div>
      </div>
      <div class="signal-value">${esc(sig.value || '—')}</div>
      <div class="signal-desc">${esc(sig.description || '')}</div>
    `;
    container.appendChild(card);
  });

  const summary = document.getElementById('signal-summary');
  if (summary) {
    summary.innerHTML = `
      <span style="color:#10b981; font-weight:700;">${bullish} Bullish</span> &nbsp;|&nbsp;
      <span style="color:#ef4444; font-weight:700;">${bearish} Bearish</span> &nbsp;|&nbsp;
      <span style="color:#94a3b8; font-weight:700;">${neutral} Neutral</span>
    `;
  }
}

// ── AI Synthesis ────────────────────────────────────────────────────────────
function renderSynthesis(synthesis) {
  setText('exec-summary',         synthesis.executive_summary   || '—');
  setText('tech-narrative',       synthesis.technical_narrative || '—');
  setText('news-narrative',       synthesis.news_narrative       || '—');
  setText('opportunity-analysis', synthesis.opportunity_analysis || '—');
  setText('risk-analysis',        synthesis.risk_analysis        || '—');
  setText('investor-note',        synthesis.investor_note        || '—');

  // Key signals tags
  const wrap = document.getElementById('key-signals-wrap');
  if (wrap) {
    wrap.innerHTML = '';
    (synthesis.key_signals || []).forEach(sig => {
      const tag = document.createElement('span');
      tag.style.cssText = 'padding:5px 14px; border-radius:20px; font-size:12px; font-weight:600; background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.2); color:#3b82f6;';
      tag.textContent = sig;
      wrap.appendChild(tag);
    });
  }
}

// ── Catalysts & Risk Factors ────────────────────────────────────────────────
function renderCatalystsAndRisks(synthesis) {
  const catalysts = synthesis.positive_catalysts || [];
  const risks     = synthesis.risk_factors || [];

  const catList = document.getElementById('catalyst-list');
  if (catList) {
    catList.innerHTML = catalysts.length
      ? catalysts.map(c => `
          <div class="catalyst-item">
            <span class="catalyst-icon">✅</span>
            <span>${esc(c)}</span>
          </div>`).join('')
      : '<div class="catalyst-item"><span class="catalyst-icon">—</span><span>No positive catalysts identified from current data.</span></div>';
  }

  const riskList = document.getElementById('risk-list');
  if (riskList) {
    riskList.innerHTML = risks.length
      ? risks.map(r => `
          <div class="risk-item">
            <span class="risk-icon">⚠️</span>
            <span>${esc(r)}</span>
          </div>`).join('')
      : '<div class="risk-item"><span class="risk-icon">—</span><span>No specific risk factors identified at this time.</span></div>';
  }
}

// ── News Section ────────────────────────────────────────────────────────────
function renderNews(news) {
  const available = news.data_available;
  const overall   = news.overall_sentiment || 'Neutral';

  // Overall badge
  const badge = document.getElementById('news-overall-badge');
  if (badge) {
    badge.textContent = available ? `${overall} Sentiment` : 'No Data';
    const colors = { Positive: '#10b981', Negative: '#ef4444', Neutral: '#94a3b8' };
    badge.style.color = colors[overall] || '#94a3b8';
    badge.style.background = available ? `${colors[overall]}22` : 'rgba(148,163,184,0.1)';
    badge.style.border = `1px solid ${colors[overall] || '#94a3b8'}44`;
    badge.style.borderRadius = '20px';
  }

  if (!available || news.total_articles === 0) {
    toggleEl('no-news-state', true);
    toggleEl('news-grid', false);
    toggleEl('news-sentiment-section', false);
    toggleEl('themes-section', false);
    return;
  }

  toggleEl('no-news-state', false);

  // Themes
  const themes = news.themes || [];
  if (themes.length > 0) {
    toggleEl('themes-section', true);
    const wrap = document.getElementById('themes-wrap');
    if (wrap) {
      wrap.innerHTML = themes.map(t => `<span class="theme-tag">${esc(t)}</span>`).join('');
    }
  }

  // Sentiment bar
  const total = news.total_articles || 1;
  const posPct  = ((news.positive_count || 0) / total * 100);
  const negPct  = ((news.negative_count || 0) / total * 100);
  const neutPct = 100 - posPct - negPct;

  setTimeout(() => {
    setWidth('news-pos-bar',  `${posPct}%`);
    setWidth('news-neut-bar', `${neutPct}%`);
    setWidth('news-neg-bar',  `${negPct}%`);
  }, 400);

  setText('news-pos-cnt',  news.positive_count  || 0);
  setText('news-neut-cnt', news.neutral_count   || 0);
  setText('news-neg-cnt',  news.negative_count  || 0);

  // Articles
  const grid = document.getElementById('news-grid');
  if (grid) {
    grid.innerHTML = '';
    (news.articles || []).forEach(article => {
      const card = document.createElement('div');
      card.className = 'news-card';
      const date = article.publishedAt ? new Date(article.publishedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '';
      card.innerHTML = `
        <div class="news-card-top">
          <div class="news-source">${esc(article.source || 'Unknown')}</div>
          <div class="news-sentiment-badge ${esc(article.sentiment)}">${esc(article.sentiment)}</div>
        </div>
        <div class="news-title">${esc(article.title || '')}</div>
        ${article.description ? `<div class="news-desc">${esc(article.description)}</div>` : ''}
        <div class="news-date">${date}</div>
      `;
      if (article.url) {
        card.style.cursor = 'pointer';
        card.addEventListener('click', () => window.open(article.url, '_blank', 'noopener'));
        card.setAttribute('title', 'Click to open article');
      }
      grid.appendChild(card);
    });
  }
}

// ── Explainable AI ──────────────────────────────────────────────────────────
function renderXAI(synthesis, fusion) {
  setText('xai-explainability', synthesis.explainability || '—');

  const tbody = document.getElementById('breakdown-body');
  if (!tbody) return;
  tbody.innerHTML = '';

  const breakdown = fusion.breakdown || [];
  breakdown.forEach((row, idx) => {
    const score = row.raw_score || 0;
    const barColor = score > 0 ? '#10b981' : score < 0 ? '#ef4444' : '#475569';
    const barWidth = Math.min(50, Math.abs(score) * 50);
    const isTotal = row.indicator === 'FINAL COMBINED SCORE';

    const tr = document.createElement('tr');
    if (isTotal) tr.style.cssText = 'background:rgba(59,130,246,0.08);';
    tr.innerHTML = `
      <td style="${isTotal ? 'color:var(--text-primary);font-weight:800;' : ''}">${esc(row.indicator || '')}</td>
      <td style="color:${row.signal === '—' ? 'var(--text-dim)' : 'var(--text-secondary);'}">${esc(row.signal || '—')}</td>
      <td style="color:${score > 0 ? '#10b981' : score < 0 ? '#ef4444' : 'var(--text-secondary)'};">
        ${score > 0 ? '+' : ''}${score.toFixed(3)}
        <span class="score-bar-inline" style="width:${barWidth}px; background:${barColor}; opacity:0.7;"></span>
      </td>
      <td>${row.weight || '—'}</td>
      <td style="color:var(--text-muted);">${isTotal ? '—' : (score * (row.weight || 1)).toFixed(3)}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ══ CHART RENDERING ══════════════════════════════════════════════════════════

function destroyAllCharts() {
  Object.keys(charts).forEach(k => {
    if (charts[k]) { charts[k].destroy(); charts[k] = null; }
  });
}

// ── Price Chart ─────────────────────────────────────────────────────────────
function renderPriceChart(cd, currentPrice) {
  const ctx = document.getElementById('price-chart');
  if (!ctx || !cd) return;

  const labels = cd.dates || [];
  const prices = cd.close  || [];

  // Build gradient fill
  const chart2d = ctx.getContext('2d');
  const gradFill = chart2d.createLinearGradient(0, 0, 0, 280);
  gradFill.addColorStop(0, 'rgba(59,130,246,0.18)');
  gradFill.addColorStop(1, 'rgba(59,130,246,0.0)');

  const gradBB = chart2d.createLinearGradient(0, 0, 0, 280);
  gradBB.addColorStop(0, 'rgba(16,185,129,0.06)');
  gradBB.addColorStop(1, 'rgba(16,185,129,0.0)');

  charts.price = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        // BB Upper
        {
          label: 'BB Upper',
          data: cd.bb_upper || [],
          borderColor: 'rgba(16,185,129,0.35)',
          borderWidth: 1,
          borderDash: [4, 4],
          pointRadius: 0,
          fill: '+1',
          backgroundColor: gradBB,
          tension: 0.3,
          order: 4,
        },
        // BB Lower
        {
          label: 'BB Lower',
          data: cd.bb_lower || [],
          borderColor: 'rgba(16,185,129,0.35)',
          borderWidth: 1,
          borderDash: [4, 4],
          pointRadius: 0,
          fill: false,
          tension: 0.3,
          order: 5,
        },
        // Price
        {
          label: 'Price',
          data: prices,
          borderColor: '#f1f5f9',
          borderWidth: 2.5,
          pointRadius: 0,
          fill: true,
          backgroundColor: gradFill,
          tension: 0.2,
          order: 1,
        },
        // SMA 20
        {
          label: 'SMA 20',
          data: cd.sma20 || [],
          borderColor: '#3b82f6',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0.3,
          order: 2,
        },
        // SMA 50
        {
          label: 'SMA 50',
          data: cd.sma50 || [],
          borderColor: '#f59e0b',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0.3,
          order: 3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(8,14,26,0.95)',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          padding: 12,
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw?.toFixed(2) || 'N/A'}`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { maxTicksLimit: 10, font: { size: 11 } },
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.06)' },
          ticks: { font: { size: 11 }, callback: (v) => v.toFixed(2) },
          position: 'right',
        },
      },
      animation: { duration: 800, easing: 'easeInOutQuart' },
    },
  });
}

// ── RSI Chart ───────────────────────────────────────────────────────────────
function renderRSIChart(cd) {
  const ctx = document.getElementById('rsi-chart');
  if (!ctx || !cd) return;

  const chart2d = ctx.getContext('2d');
  const gradRSI = chart2d.createLinearGradient(0, 0, 0, 160);
  gradRSI.addColorStop(0, 'rgba(139,92,246,0.2)');
  gradRSI.addColorStop(1, 'rgba(139,92,246,0.0)');

  charts.rsi = new Chart(ctx, {
    type: 'line',
    data: {
      labels: cd.dates || [],
      datasets: [
        {
          label: 'RSI',
          data: cd.rsi || [],
          borderColor: '#8b5cf6',
          borderWidth: 2,
          pointRadius: 0,
          fill: true,
          backgroundColor: gradRSI,
          tension: 0.3,
        },
        // Overbought line at 70
        {
          label: 'Overbought (70)',
          data: (cd.dates || []).map(() => 70),
          borderColor: 'rgba(239,68,68,0.5)',
          borderWidth: 1,
          borderDash: [4, 4],
          pointRadius: 0,
          fill: false,
        },
        // Oversold line at 30
        {
          label: 'Oversold (30)',
          data: (cd.dates || []).map(() => 30),
          borderColor: 'rgba(16,185,129,0.5)',
          borderWidth: 1,
          borderDash: [4, 4],
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(8,14,26,0.95)',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          padding: 10,
          filter: (item) => item.datasetIndex === 0,
          callbacks: {
            label: (ctx) => ` RSI: ${ctx.raw?.toFixed(1) || '—'}`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.03)' },
          ticks: { maxTicksLimit: 6, font: { size: 10 } },
        },
        y: {
          min: 0, max: 100,
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { font: { size: 10 }, stepSize: 20 },
          position: 'right',
        },
      },
      animation: { duration: 700 },
    },
  });
}

// ── MACD Chart ──────────────────────────────────────────────────────────────
function renderMACDChart(cd) {
  const ctx = document.getElementById('macd-chart');
  if (!ctx || !cd) return;

  const histColors = (cd.macd_histogram || []).map(v =>
    v === null ? 'transparent' : v >= 0 ? 'rgba(16,185,129,0.65)' : 'rgba(239,68,68,0.65)'
  );

  charts.macd = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: cd.dates || [],
      datasets: [
        {
          label: 'Histogram',
          data: cd.macd_histogram || [],
          backgroundColor: histColors,
          borderWidth: 0,
          order: 3,
        },
        {
          label: 'MACD',
          data: cd.macd || [],
          type: 'line',
          borderColor: '#3b82f6',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0.3,
          order: 1,
        },
        {
          label: 'Signal',
          data: cd.macd_signal || [],
          type: 'line',
          borderColor: '#f97316',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0.3,
          order: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(8,14,26,0.95)',
          borderColor: 'rgba(255,255,255,0.1)',
          borderWidth: 1,
          padding: 10,
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw?.toFixed(4) || '—'}`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.03)' },
          ticks: { maxTicksLimit: 6, font: { size: 10 } },
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { font: { size: 10 }, callback: (v) => v.toFixed(3) },
          position: 'right',
        },
      },
      animation: { duration: 700 },
    },
  });
}

// ══ UTILITY FUNCTIONS ═════════════════════════════════════════════════════

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text ?? '—';
}

function setWidth(id, width) {
  const el = document.getElementById(id);
  if (el) el.style.width = width;
}

function toggleEl(id, show) {
  const el = document.getElementById(id);
  if (!el) return;
  if (show) el.classList.remove('hidden');
  else el.classList.add('hidden');
}

function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatNum(n) {
  if (n === null || n === undefined) return '—';
  return Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatMarketCap(n) {
  if (!n) return '';
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9)  return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6)  return `$${(n / 1e6).toFixed(2)}M`;
  return `$${n.toLocaleString()}`;
}

function getCurrencySymbol(currency) {
  const map = { USD: '$', INR: '₹', EUR: '€', GBP: '£', JPY: '¥', CAD: 'CA$', AUD: 'A$' };
  return map[currency] || (currency ? currency + ' ' : '$');
}

function animateCounter(id, from, to, duration, formatter) {
  const el = document.getElementById(id);
  if (!el) return;
  const start = performance.now();
  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const val = from + (to - from) * eased;
    el.textContent = formatter ? formatter(val) : Math.round(val);
    if (progress < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}
