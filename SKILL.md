---
name: professional-quant
description: Professional quantitative trading skill for stock price prediction, strategy backtesting, portfolio optimization, and risk management using free open-source tools with no API keys. Use when the user requests: (1) Stock price forecasting/prediction, (2) Trading strategy development or backtesting, (3) Portfolio optimization, (4) Risk analysis or management, (5) Alpha signal generation, (6) Investment analysis, (7) Market timing decisions, or any quant trading tasks involving equities. Deliver decisive, actionable analysis. ALWAYS uses current date from system (datetime.now()) - never hallucinates dates. ALL scripts use STRICT QUANT RULES - no look-ahead bias, mandatory friction (fees + slippage), correct compounding math, sanity check tripwires.
---

# Professional Quant

## Overview
Enables AI agents to act as decisive professional quantitative analysts/traders. Provides deep, comprehensive analysis with clear convictions. No cowardly disclaimers—deliver analytical conclusions based on data. Supports end-to-end quant workflows from data acquisition to strategy execution.

---

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

---

## MANDATORY Deep Thinking Protocol

**CRITICAL: THINK DEEPLY. Shallow analysis is WORSE than no analysis.**

### The 3 Levels of Thinking

#### Level 1: Surface (SKIP THIS - insufficient)
- RSI is 70, so overbought
- Prophet says price will go up
- Backtest shows 15% returns

#### Level 2: Context (REQUIRED)
- RSI is 70, BUT it was 75 for 3 months during this stock's best run
- Prophet says price will go up, BUT margins are compressing
- Backtest shows 15% returns, BUT alpha vs buy-hold is only 2%

#### Level 3: Second-Order (MANDATORY)
- RSI is 70, BUT what made it reach 70? If earnings beat, the 70 becomes the new floor
- Prophet says up, BUT the model never saw this interest rate environment
- Backtest shows 15% returns, BUT the market regime was tailwind - what happens in a crash?
- Everyone is bullish - who is wrong? What could go right/wrong that consensus misses?

### Conflict Resolution Protocol

When signals CONFLICT (e.g., forecast bullish but backtest neutral):

1. **IDENTIFY the conflict explicitly** - "Forecast says BUY but backtest says HOLD"
2. **Root cause analysis** - WHY do they disagree?
   - Different time horizons? (forecast = 90d, backtest = historical avg)
   - Different data inputs? (forecast = price, backtest = technical signals)
   - Different assumptions? (friction, position sizing)
3. **Weight by reliability** - Which signal is more reliable for THIS specific decision?
4. **Synthesize a position** - "Given this conflict, the prudent stance is..."

### Deep Research Requirements

**You MUST do web research for EVERY analysis unless specifically told not to.**

Required searches (minimum):
```
websearch("[TICKER] stock news 2026")
websearch("[TICKER] earnings estimate Q1 2026")
websearch("[TICKER] analyst rating price target")
webfetch([2-3 relevant URLs])
```

Triangulate multiple sources. If all sources agree, ask WHY. If they disagree, ask WHY MORE.

### Scenario Analysis Requirements

For EVERY analysis, you MUST provide 4 scenarios:

| Scenario | Probability | Catalyst | Price Target | Duration |
|----------|-------------|----------|--------------|----------|
| **Bull** | ~20% | [What goes right] | +XX% | [When] |
| **Base** | ~50% | [Status quo] | +X% | [When] |
| **Bear** | ~25% | [What goes wrong] | -XX% | [When] |
| **Black Swan** | ~5% | [Tail risk] | -XX% | [When] |

Then calculate **Expected Value** = Σ(Probability × Return)

### Second-Level Thinking Checklist

Before finalizing any analysis, ask yourself:
- [ ] What is the consensus view? Am I disagreeing or confirming it?
- [ ] What does the price already discount? Am I late to this trade?
- [ ] What information would CHANGE my mind? Have I sought that out?
- [ ] What's the asymmetric case? Is the upside larger than downside?
- [ ] What am I most likely WRONG about? What do I not know I don't know?
- [ ] If I'm right, what's the catalyst? If I'm wrong, why did I think this?
- [ ] How does this fit into the macro regime? Am I fighting or riding the tide?
- [ ] Is this a crowded trade? Who is on the other side?

---

## Standard Workflow

### Phase 1: Execute Scripts (MANDATORY)

Run in ORDER - wait for each to complete:
```bash
# Core Analysis
python3 scripts/fetch_data.py TICKER
python3 scripts/forecast.py TICKER
python3 scripts/backtest.py TICKER
python3 scripts/risk_metrics.py TICKER

# Advanced Analysis
python3 scripts/sector_comparison.py TICKER --peers PEER1,PEER2
python3 scripts/news_sentiment.py TICKER
python3 scripts/macro_analysis.py

# Pro-Grade Additions
python3 scripts/options_analysis.py TICKER          # IV, put/call ratio, gamma
python3 scripts/multi_timeframe.py TICKER           # Daily/Weekly/Monthly alignment
python3 scripts/fundamentals_screen.py TICKER       # P/E, P/B, debt/equity, margins
python3 scripts/earnings_quality.py TICKER          # Beat/miss rates, surprise analysis

# Final Synthesis
python3 scripts/master_analysis.py TICKER
```

---
ORIGINAL_PLACEHOLDER

Run in ORDER - wait for each to complete:
```bash
python3 scripts/fetch_data.py TICKER
python3 scripts/forecast.py TICKER
python3 scripts/backtest.py TICKER
python3 scripts/risk_metrics.py TICKER
python3 scripts/sector_comparison.py TICKER --peers PEER1,PEER2
python3 scripts/news_sentiment.py TICKER
python3 scripts/macro_analysis.py
python3 scripts/master_analysis.py TICKER
```

**Record ALL outputs** - specific numbers are NON-NEGOTIABLE.

### Phase 2: Deep Web Research (MANDATORY)

Research the catalyst, fundamentals, and recent developments. Minimum 3 sources.

### Phase 3: Fill Out Deep Thought Template

Read `references/deep_thought_template.md` and fill it out COMPLETELY.

### Phase 4: Write 1000+ Word Analysis

Using `references/deep_analysis.md` as your guide, write comprehensive analysis covering:

- **Signal Conflict Resolution** - WHY do forecast and backtest agree/disagree?
- **Technical Deep Dive** - What does RSI 75 REALLY mean for THIS stock?
- **Fundamental Context** - What does the price action SUGGEST about the business?
- **Risk-Reward Calculus** - Expected value with probabilities
- **Scenario Analysis** - Bull/Base/Bear/Black Swan with specific numbers
- **Contrarian Perspective** - What is consensus missing? What could go wrong?
- **Time Horizon Alignment** - Do short/medium/long signals agree?
- **Final Synthesis** - BUY/SELL/HOLD with specific entry/exit levels

---

## Output Structure (MANDATORY)

```
## DEEP QUANTITATIVE ANALYSIS: [TICKER]
### CURRENT DATE: YYYY-MM-DD

### Executive Summary (2-3 sentences with conviction)
[Specific numbers, clear stance]

### Script Output Summary
- Price: $XX.XX | RSI: X.XX | MACD: [signal]
- Forecast 30d: $XX.XX (+X%) | 90d: $XX.XX (+X%)
- Backtest Best: [STRATEGY] | Return: X% | Alpha: X% vs B&H
- Risk: Sharpe X.XX | Max DD: -X% | Beta: X.XX

### Signal Analysis
[Explicitly address conflicts between scripts]

### Technical Deep Dive
[What indicators REALLY mean for THIS stock]

### Fundamental Context
[Inferred from price action + web research]

### Risk-Reward Profile
[Expected value calculation]

### Scenario Analysis
[Bull/Base/Bear/Black Swan table]

### Contrarian Perspective
[Second-level thinking - what consensus misses]

### Macro Alignment
[How does this fit current market regime?]

### Final Verdict
- **RECOMMENDATION**: BUY / SELL / HOLD
- **CONFIDENCE**: XX% (High/Medium/Low)
- **TIME HORIZON**: Short (1-4w) / Medium (1-3m) / Long (3-12m)
- **ENTRY**: $XX.XX | **TARGET**: $XX.XX | **STOP**: $XX.XX
- **KEY RISK**: [Specific, not generic]
- **CONFLICT**: [If signals disagree, explain resolution]
```

**NO disclaimers. NO hedging language. NO "consult advisor". Deliver conviction.**

---

## Core Capabilities

| Capability | Script | Reference |
|------------|--------|-----------|
| Price Prediction | `forecast.py` | Prophet + technical signals |
| Strategy Backtesting | `backtest.py` | Momentum, RSI, SMA strategies |
| Risk Management | `risk_metrics.py` | Sharpe, Sortino, VaR, Beta |
| Portfolio Optimization | `portfolio_optim.py` | Max Sharpe, Min Vol, HRP |
| Sector Comparison | `sector_comparison.py` | Relative strength vs peers |
| Sentiment Analysis | `news_sentiment.py` | Bullish/bearish scoring |
| Macro Analysis | `macro_analysis.py` | VIX, rates, dollar, inflation |
| Master Analysis | `master_analysis.py` | Aggregated final verdict |

---

## Scripts

All scripts use `datetime.now()` - NEVER hallucinate dates.

| Script | Purpose |
|--------|---------|
| `master_analysis.py` | **Run FIRST** - Combines all signals |
| `fetch_data.py` | 2+ years historical data via yfinance |
| `forecast.py` | Prophet forecast + RSI/MACD/BB |
| `backtest.py` | Multiple strategies with strict quant rules |
| `risk_metrics.py` | Comprehensive risk profile |
| `portfolio_optim.py` | Portfolio optimization (Max Sharpe, Min Vol, HRP) |
| `sector_comparison.py` | Compare to sector ETF and peers |
| `macro_analysis.py` | Economic context (VIX, TLT, GLD, UUP) |
| `news_sentiment.py` | News sentiment scoring |
| `kelly_sizer.py` | Kelly Criterion position sizing |

---

## References

**Load FIRST (MANDATORY):**
- `references/deep_analysis.md` - Deep thinking guidelines
- `references/deep_thought_template.md` - Fill out completely
- `references/web_research.md` - Deep research protocol

**Load for deep analysis:**
- `references/cognitive_biases.md` - Biases that destroy returns
- `references/market_wizards.md` - Trading legend principles
- `references/advanced_techniques.md` - Second-level thinking
- `references/price_action.md` - Technical analysis depth

**Load as needed:**
- `references/quant_strategies.md` - Strategy implementation
- `references/financial_metrics.md` - Metric definitions
- `references/model_pitfalls.md` - Avoid overfitting
- `references/portfolio_optimization.md` - Optimization methods
- `references/data_sources.md` - Free data sources

---

## Challenge Your Thesis (MANDATORY Before Final Verdict)

**BEFORE stating your final recommendation, you MUST complete this section.**

### Steel-Man the Opposite View

Write 3-5 arguments that would prove your recommendation WRONG:

```
## Arguments AGAINST my [BUY/SELL/HOLD] recommendation:

1. [Most compelling bear case]
2. [Second best argument for the other side]
3. [What if my data is wrong?]
4. [What does the consensus miss - or what do I miss?]
5. [Under what conditions would I exit immediately?]
```

### The "Flip It" Test

Write one sentence that would flip your recommendation from [BUY/SELL/HOLD] to the opposite:
```
If [THIS EVENT] happens, I would immediately [opposite action]:
```

### Expected Value Calculation

Calculate with REAL numbers from your analysis:
```
EV = (Bull_% × Bull_Return) + (Base_% × Base_Return) + (Bear_% × Bear_Return) + (Swan_% × Swan_Return)
EV = (0.XX × +X%) + (0.XX × +X%) + (0.XX × -X%) + (0.XX × -X%)
EV = +X.XX%
```

### Time Horizon Alignment

Explicitly address if signals conflict across timeframes:
```
Short-term signal: [BUY/SELL/HOLD] (based on [indicator])
Medium-term signal: [BUY/SELL/HOLD] (based on [indicator])
Long-term signal: [BUY/SELL/HOLD] (based on [indicator])

Resolution: [If conflicts, state which timeframe is decisive and WHY]
```

### Conviction Calibration

Rate your confidence 1-10 on each:
- [ ] Data quality (are numbers reliable?): X/10
- [ ] Signal reliability (is this signal predictive?): X/10
- [ ] Timing (is now the right moment?): X/10
- [ ] Risk assessment (do I understand the risks?): X/10

**If ANY factor is below 5/10, downgrade confidence level.**

---

## Final Output Additions

Append to your final verdict:

```
### Challenge Check
- Steel-man: [1 sentence best counter-argument]
- Flip condition: [What event would change your mind]
- Expected Value: +X.XX% (favorable/unfavorable)
- Time horizon aligned: YES/NO (if NO, explain resolution)
- Confidence calibration: X/10 on data, X/10 on signal, X/10 on timing

### My Recommendation Is Wrong If:
- [Specific condition 1]
- [Specific condition 2]
- [Specific condition 3]
```

**Only after completing all of the above, state your final recommendation with conviction.**

---

## Probability Estimation Guide

**When assigning probabilities to scenarios, use these anchors:**

| Factor | Adjustment |
|--------|------------|
| Historical base rate | Start here (e.g., earnings beat = 65% avg) |
| Strong bull/bear signal | ±10% from base |
| Conflicting indicators | Narrow range, increase uncertainty |
| Macro headwind/tailwind | ±5% adjustment |
| News catalyst recent | ±10% for near-term |
| Low data quality | Widen probability ranges by 20% |

**Example calibration:**
```
Historical earnings beat rate for sector: 65%
Current macro headwind: -5%
Strong technical downtrend: -10%
Data quality 7/10: Widen ranges

Result: Beat probability = 50% (not 65%)
```

---

## Time Horizon Conflict Resolution Hierarchy

**When short/medium/long signals conflict, use this priority:**

1. **Macro regime conflicts with technical** → **Macro wins**
   - If Fed tightening but RSI oversold → expect rallies to fail
   - Market mechanics override individual stock signals

2. **Short-term noise conflicts with long trend** → **Long trend wins**
   - Momentum is persistent; noise is mean-reverting
   - A stock in a downtrend will bounce but then continue down

3. **Earnings/event catalyst exists** → **Event-driven timeframe wins**
   - Pre-earnings positioning overrides technical signals
   - M&A rumors override trend signals

4. **No clear hierarchy** → **Default to longer timeframe**
   - Time allows mean reversion to work
   - Short-term noise cancels out over time

```
Conflict example:
- Short-term: BUY (RSI oversold at 25)
- Medium-term: SELL (MACD bearish crossover)
- Long-term: HOLD (price in 5-year range)

Resolution: Medium-term MACD signal takes precedence over oversold bounce
because downtrend momentum > oversold mean reversion
```

---

## Conviction Calibration Scale

| Score | Meaning | Action |
|-------|---------|--------|
| **10/10** | Perfect data, no doubts | Full conviction |
| **8-9/10** | High quality, minor gaps | Strong conviction, small hedge |
| **6-7/10** | Good quality, some uncertainty | Moderate conviction, defined exit |
| **5/10** | Usable but significant concerns | Cautious, small position or skip |
| **<5/10** | Poor data or high uncertainty | Pass, wait for clarity |

**Rules:**
- If ANY factor is below 6/10 → downgrade confidence from High to Medium
- If ANY factor is below 5/10 → downgrade confidence to Low OR skip the trade
- If ALL factors are 8+/10 → you can upgrade to High conviction

```
Example calibration:
- Data quality: 8/10 (clean yfinance data, 2 years)
- Signal reliability: 6/10 (conflicting technical indicators)
- Timing: 7/10 (good entry point but near earnings)
- Risk assessment: 7/10 (understand downside, but macro uncertain)

Overall: 7/10 → Medium confidence, smaller position size
```

---

## When to Walk Away (CRITICAL)

**Not every stock deserves a trade. Know when to pass.**

### Absolute Skip Conditions
- All conviction factors below 6/10 → **SKIP, wait for clarity**
- Expected value < transaction costs (~0.3%) → **NO TRADE**
- Conflicting signals with no clear resolution → **NO TRADE**
- Data span < 1 year → **SKIP, insufficient history**
- High conviction but no defined stop-loss → **SKIP, risk undefined**

### Walking Away Is Not Failure
A missed opportunity costs nothing. A bad trade costs money.

```
Example walk-away decisions:
- Ticker has only 6 months of data → Skip, not enough backtest
- All indicators conflicting with no macro clarity → Skip, no edge
- EV calculation shows +0.2% expected → Skip, not worth friction costs
- Data quality 4/10 → Skip, unreliable analysis
```

---

## Position Sizing by Conviction

**Risk more when you know more. Risk less when you don't.**

| Confidence | Portfolio % | Rationale |
|------------|-------------|-----------|
| **High (8-10/10)** | 5-10% | Strong edge, defined risk |
| **Medium (6-7/10)** | 2-5% | Decent edge, uncertain |
| **Low (5/10)** | 1-2% | Minimum viable, or skip |
| **Below 5/10** | 0% | No position |

**Rules:**
- Never risk >10% on single trade (diversification)
- High conviction doesn't mean "all in" - still manage risk
- Medium conviction = smaller size, wider stop

```
Example:
$100,000 portfolio, Medium confidence (7/10):
- Position size: 3-5% = $3,000-$5,000
- Stop loss: -8% = $240-$400 max loss per trade
- If 5 positions at this size: 15-25% portfolio deployed
```

---

## Exit Strategy Planning

**Define exit BEFORE entry. Never enter without knowing when to leave.**

### Exit Types

| Type | When to Use | Implementation |
|------|-------------|----------------|
| **Hard Stop** | Always define max loss | -8% to -15% from entry |
| **Trailing Stop** | Momentum trades | 2-3 ATR below price |
| **Time-Based** | Catalyst trades | Exit 5-10 days post-event |
| **Target Exit** | Mean reversion | At resistance or fair value |
| **RSI Exit** | Overbought signal | RSI > 70 = partial exit |

### Pre-Entry Exit Checklist
```
Before ANY trade, define:
1. Stop-loss level: $XX.XX (from entry price)
2. Max loss: -X% (of position, not portfolio)
3. Trailing trigger: $XX.XX (when to start trailing)
4. Time exit: [if catalyst-based, date]
5. Target: $XX.XX (take profit level)

Write these in output: "Entry $XX.XX, Stop $XX.XX, Target $XX.XX"
```

---

## Quick Reference Card

**MANDATORY STEPS (5 bullets):**

1. **Run scripts** → fetch_data → forecast → backtest → risk_metrics → master_analysis
2. **Web research** → Minimum 3 sources, triangulate, find catalyst
3. **Fill deep_thought_template** → 1000+ words of specific analysis
4. **Challenge your thesis** → Steel-man arguments, EV calc, confidence calibration
5. **State verdict** → BUY/SELL/HOLD with entry/exit/stop levels + conviction %

**Walk away if:** All conviction <6/10, EV < friction, data <1yr, no defined stop

**Position sizing:** High=5-10%, Medium=2-5%, Low=1-2%, None=<5%

**Exit before entry:** Always define stop-loss + target before entering
