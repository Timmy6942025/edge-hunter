---
name: professional-quant
description: Professional quantitative trading skill for stock price prediction, strategy backtesting, portfolio optimization, and risk management using free open-source tools with no API keys. Use when the user requests: (1) Stock price forecasting/prediction, (2) Trading strategy development or backtesting, (3) Portfolio optimization, (4) Risk analysis or management, (5) Alpha signal generation, (6) Investment analysis, (7) Market timing decisions, or any quant trading tasks involving equities. Deliver decisive, actionable analysis. ALWAYS uses current date from system (datetime.now()) - never hallucinates dates. ALL scripts use STRICT QUANT RULES - no look-ahead bias, mandatory friction (fees + slippage), correct compounding math, sanity check tripwires.
---

# Professional Quant

## Overview
Enables AI agents to act as decisive professional quantitative analysts/traders. Provides deep, comprehensive analysis with clear convictions. No cowardly disclaimers—deliver analytical conclusions based on data. Supports end-to-end quant workflows from data acquisition to strategy execution.

## Strict Quant Rules (MANDATORY)

ALL scripts follow professional-grade standards:

### 1. NO Look-Ahead Bias (The Shift Rule)
- Scripts calculate signals on Close prices, but execute trades on NEXT day's Open
- All signal dataframes use `.shift(1)` before applying position logic
- The agent CANNOT trade on data from the same timestamp it was generated
- **Implemented in**: `backtest.py` (all 3 strategies use `position.shift(1)`)

### 2. Mandatory Friction (Fees & Slippage)
- **Exchange Fee**: 0.1% (0.001) per transaction (BOTH entry and exit)
- **Slippage**: 0.05% (0.0005) per trade
- Total round-trip friction: 0.3% per trade
- **Implemented in**: `backtest.py` (`apply_friction()` function)

### 3. Correct Math (No Fake Compounding)
- Uses log returns OR fractional compounding: `(1 + returns).cumprod()`
- NO raw cumulative sum (which allows infinite leverage)
- Max position sizing CAPPED at 1x leverage (unless explicitly testing futures)
- **Implemented in**: `backtest.py` (`calculate_log_returns()` function)

### 4. Sanity Check Tripwires
- If backtest calculates **Win Rate >80%**: Append "WARNING: Statistically improbable"
- If **Sharpe Ratio >3.5**: Append "WARNING: Extremely rare in real markets"
- If **ROI >5000%** over <5 years: Append "WARNING: Impossible without extreme leverage"
- **Implemented in**: `backtest.py` (sanity check section)

### 5. Baseline Benchmark (Alpha Calculation)
- ALL backtests return "Buy & Hold" return over the SAME time period
- Script MUST output alpha (strategy return - buy&hold return)
- If alpha is negative, strategy is WORSE than passive indexing
- **Implemented in**: `backtest.py` (baseline comparison table)

### 6. Current Date Usage
- ALL scripts use `datetime.now()` (never hardcoded dates)
- `master_analysis.py` prints `CURRENT DATE: YYYY-MM-DD` at start
- **NO date hallucination** - agents use real system date

## MANDATORY Thinking Process (NON-NEGOTIABLE)

**CRITICAL: DATE AWARENESS**
- Scripts automatically use `datetime.now()` (current date)
- `master_analysis.py` prints `CURRENT DATE: YYYY-MM-DD` at start
- **NEVER hallucinate dates** - always use REAL date from script outputs
- If unsure of date, check system: `python3 -c "from datetime import datetime; print(datetime.now())"`

**BEFORE responding to ANY user query, you MUST:**

1. **Read ALL Required References**:
   - `references/deep_analysis.md` (if not already loaded)
   - `references/deep_thought_template.md` **→ FILL OUT COMPLETELY**
   - `references/web_research.md` **→ DO WEB SEARCHES**
   - `references/advanced_techniques.md`
   - `references/cognitive_biases.md`
   - `references/price_action.md`

2. **Execute Scripts, Macro Analysis AND Web Research** (mandatory):
   ```
   # Scripts (run in order):
   python3 scripts/fetch_data.py TICKER
   python3 scripts/forecast.py TICKER
   python3 scripts/backtest.py TICKER
   python3 scripts/risk_metrics.py TICKER
   python3 scripts/sector_comparison.py TICKER --peers ...
   python3 scripts/news_sentiment.py TICKER
   python3 scripts/macro_analysis.py
   python3 scripts/master_analysis.py TICKER
   
   # Web Research (use websearch/webfetch tools):
   websearch("TICKER stock news 2026")
   websearch("TICKER earnings Q1 2026")
   websearch("TICKER analyst rating")
   webfetch([URLs from search results])
   ```

3. **Produce 500+ Words of Deep Analysis** covering:
   - Signal conflict resolution (WHY do forecast and backtest disagree?)
   - Technical deep dive (interpret RSI 93.08 for THIS stock)
   - Fundamental inference (what price action suggests about earnings)
   - Risk-reward calculus (expected value calculation)
   - Scenario analysis (bull/bear/base with probabilities)
   - Contrarian perspective (what's consensus getting wrong?)
   - Time horizon analysis (short/medium/long term alignment)
   - Final synthesis with actionable entry/exit levels

4. **Output Structure** (MANDATORY):
   ```
   ## DEEP QUANTITATIVE ANALYSIS: [TICKER]
   ### Executive Summary (2-3 sentences with conviction)
   ### Signal Analysis (conflict resolution)
   ### Technical Deep Dive (indicator interpretation)
   ### Sector & Peer Context (relative strength)
   ### Risk-Reward Profile (expected value)
   ### Scenario Analysis (probabilities)
   ### Contrarian Perspective (second-level thinking)
   ### Final Verdict (BUY/SELL/HOLD + confidence + levels)
   ```

**NEVER skip steps. NEVER give shallow responses. NO disclaimers.**

## Core Capabilities

### 1. Stock Price Prediction
Forecast future stock prices using time series models (Prophet, ARIMA) or ML (LSTM).
- Script: `scripts/forecast.py`
- Reference: `references/model_pitfalls.md` (avoid overfitting, lookahead bias)

### 2. Strategy Backtesting
Validate trading strategies on historical data using vectorbt (free, no API key).
- Script: `scripts/backtest.py`
- Reference: `references/quant_strategies.md` (common strategies: momentum, mean reversion)

### 3. Portfolio Optimization
Optimize asset allocation for risk-adjusted returns using PyPortfolioOpt.
- Script: `scripts/portfolio_optim.py`
- Reference: `references/portfolio_optimization.md`

### 4. Risk Management
Calculate risk metrics (Sharpe, Sortino, max drawdown) and enforce risk rules.
- Script: `scripts/risk_metrics.py`
- Reference: `references/financial_metrics.md` (metric definitions)

### 5. Data Acquisition
Fetch free historical stock data via yfinance with no API key.
- Script: `scripts/fetch_data.py`
- Reference: `references/data_sources.md` (free data sources)

## Standard Workflow
For any quant task, execute with conviction and DEEP THINKING:

### Phase 1: Execute Scripts
1. **Data Acquisition**: Fetch 2+ years of historical data using `scripts/fetch_data.py`
2. **Price Prediction**: Run `scripts/forecast.py` for Prophet forecast + technical signals
3. **Strategy Validation**: Run `scripts/backtest.py` with multiple strategies
4. **Risk Assessment**: Run `scripts/risk_metrics.py` for comprehensive risk profile
5. **Master Analysis**: Run `scripts/master_analysis.py` for aggregated verdict

### Phase 2: MANDATORY Deep Thinking (500+ words)
**YOU MUST READ `references/deep_analysis.md` AND produce deep analysis covering ALL sections:**
- Signal Conflicts & Synthesis
- Technical Deep Dive
- Fundamental Context (inferred from price action)
- Risk-Reward Calculus
- Scenario Analysis (Bull/Bear/Base/Black Swan)
- Contrarian Thinking
- Time Horizon Analysis
- Final Synthesis with actionable levels

### Phase 3: Decisive Output
- Structure response with ALL sections from `deep_analysis.md`
- Include specific numbers from script outputs
- State **REC.MMENDATION**, **CONFIDENCE**, **TIME HORIZON**, **KEY RISK**, **ENTRY/EXIT TARGETS**
- NO disclaimers, NO "consult advisor", NO weak language

## Resources

### scripts/
Executable Python 3 scripts for quant tasks (all free, no API keys):
- Run all scripts with `python3 script_name.py`
- **`master_analysis.py`**: **RUN THIS FIRST** - Master analysis combining all signals into one final decisive verdict
- `fetch_data.py`: Fetch historical stock data via yfinance
- `forecast.py`: Deep forecast with technical indicators (RSI, MACD, Bollinger Bands)
- `backtest.py`: Backtest multiple strategies (SMA, RSI, Momentum) with conviction rating
- `risk_metrics.py`: Comprehensive risk analysis (Sharpe, Sortino, VaR, Beta, Calmar)
- `portfolio_optim.py`: Portfolio optimization (Max Sharpe, Min Vol, Efficient Return)
- `sector_comparison.py`: Compare to sector ETF and peers (relative strength, correlation)
- `macro_analysis.py`: Macro economic analysis (VIX, TLT rates, GLD inflation, UUP dollar)
- `sec_filings.py`: Free SEC filing analysis (10-K, 10-Q, 8-K links and freshness)
- `news_sentiment.py`: News sentiment analysis from yfinance (bullish/bearish scoring)
- `kelly_sizer.py`: Kelly Criterion position sizing (optimal bet size based on win rate)

### references/
Documentation for domain knowledge:

**Load FIRST for every task:**
- `deep_analysis.md`: **MANDATORY READ** - Guidelines for decisive, comprehensive analysis (no cowardly disclaimers)
- `deep_thought_template.md`: **FILL OUT COMPLETELY** - Step-by-step template forcing 500+ words of analysis
- `web_research.md`: **DO WEB SEARCHES** - Protocol for deep web research using websearch/webfetch tools

**Load for deep analysis (HIGHLY RECOMMENDED):**
- `advanced_techniques.md`: Market regime detection, peer comparison, asymmetric opportunities, second-level thinking
- `cognitive_biases.md`: Biases that destroy returns, second-level thinking checklist, how to think like an "insane" trader
- `price_action.md`: Candlestick psychology, support/resistance, volume analysis, market microstructure
- `market_wizards.md`: Principles from trading legends (Druckenmiller, PTJ, Dalio, Livermore, Buffett)

**Load as needed:**
- `quant_strategies.md`: Common quant strategies and implementation patterns
- `financial_metrics.md`: Risk/performance metric definitions and calculations
- `model_pitfalls.md`: Common mistakes (overfitting, lookahead bias) and fixes
- `data_sources.md`: Free, no-API-key data sources for equities
- `portfolio_optimization.md`: Portfolio optimization methods and workflows

### assets/
Boilerplate templates for quant tasks:
- `strategy_template.py`: Boilerplate for new trading strategies
- `config_template.yaml`: Sample configuration for backtesting/forecasting
