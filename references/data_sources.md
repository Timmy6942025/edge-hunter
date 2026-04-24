# Data Sources: What's Available, What's Not, and What It Means

> **Role in this skill**: Appendix — reference for what data is available and its limitations. Data is an input, not the analysis. For how to find information beyond what these sources provide (qualitative research, primary sources, etc.), see `references/research_for_edge.md`.

---

## The Data Hierarchy

Not all data is created equal. The type of data you're working with determines what conclusions you can legitimately draw.

| Tier | Data Type | What It Captures | What It Misses | Examples |
|------|-----------|-----------------|----------------|----------|
| **1 — Price/Volume** | Market transactions | What happened, at what price, in what quantity | *Why* it happened, sentiment, fundamentals | yfinance OHLCV |
| **2 — Derived Technical** | Mathematical transforms of price | Momentum, volatility, mean-reversion signals | Causation, regime context, fundamental change | RSI, MACD, Bollinger, SMA |
| **3 — Fundamental** | Company financials | Business performance, valuation, balance sheet | Future trajectory, competitive dynamics, management quality | SEC filings (via sec_filings.py) |
| **4 — Macro/Context** | Economic environment | Rate regime, inflation, sector trends | Timing, relative attractiveness, idiosyncratic risk | macro_analysis.py, sector_rotation.py |
| **5 — Qualitative** | Non-numeric intelligence | Competitive moats, management quality, regulatory risk, narratives | Not available from scripts — requires reasoning and research | Earnings calls, industry reports, expert analysis |

**The critical insight**: Scripts give you Tiers 1-4. The variables that most often determine whether an investment thesis is correct or wrong are in **Tier 5**. See `references/qualitative_mosaic.md` for how to analyze what scripts can't measure.

---

## Available Data Sources (Script-Accessible)

### yfinance (Primary Data Engine)

The backbone of this skill's data infrastructure.

- **What it provides**: Historical OHLCV (Open, High, Low, Close, Volume) data for equities and ETFs
- **No API key required**
- **Used by**: `scripts/fetch_data.py`, `scripts/forecast.py`, `scripts/portfolio_optimizer.py`, and most other scripts
- **Coverage**: US equities, major international stocks, ETFs (including commodity, bond, and currency ETFs)
- **Delay**: 15-minute delay for free access
- **Historical depth**: Several years of daily data; intraday data available but limited

#### What yfinance Can Tell You
- Price history and basic technical patterns
- Volume trends and liquidity assessment
- Sector ETF performance for relative comparison
- Commodity/bond/FX ETFs as macro proxies

#### What yfinance Cannot Tell You
- **Real-time prices**: 15-minute delay means you're always slightly behind
- **Options data**: Limited chain data; no Greeks, no IV surface detail
- **Fundamentals**: yfinance provides some fundamental data, but it's often stale, incomplete, or inconsistent
- **Analyst estimates**: No consensus EPS, revenue estimates, or price targets
- **Institutional holdings**: No 13F data, no fund flow data
- **Short interest**: Not available through yfinance
- **Order flow / Level 2**: No market microstructure data

### vectorbt YahooData

Built-in data downloader via yfinance, optimized for backtesting workflows.

- **No API key required**
- **Used by**: `scripts/backtest.py`, `scripts/risk_metrics.py`
- **Advantage**: Seamless integration with vectorbt's backtesting engine, automatic handling of data alignment and missing values
- **Same limitations as yfinance**: This is yfinance data, just packaged differently

### SEC EDGAR (via sec_filings.py)

Primary source for company financial filings — the most authoritative fundamental data available for free.

- **What it provides**: Access to 10-K (annual) and 10-Q (quarterly) filings
- **No API key required** — uses SEC's public EDGAR system
- **Used by**: `scripts/sec_filings.py`
- **Coverage**: All US-listed companies that file with the SEC

#### What SEC Filings Can Tell You
- **10-K**: Full annual financials, risk factors, management discussion, auditor letters, legal proceedings
- **10-Q**: Quarterly financials, significant events, updated risk factors
- **8-K** (not currently scraped): Real-time event disclosures (M&A, management changes, bankruptcy)
- **Insider transactions** (Form 4 — not currently scraped): Who's buying/selling and how much
- **Institutional holdings** (13F — not currently scraped): What funds own, updated quarterly

#### What SEC Filings Cannot Tell You
- **Management tone**: The text is there, but extracting sentiment requires reading it (see `references/research_for_edge.md`)
- **Forward guidance**: Filings are backward-looking; guidance is on earnings calls
- **Competitive dynamics**: Companies describe their own business, not the industry landscape
- **Channel checks**: No data on real-time sales, customer behavior, or supply chain conditions

### Macro Proxies (via macro_analysis.py)

ETFs that serve as proxies for macro-economic conditions.

- **VIX** (^VIX): Volatility regime — risk-on vs risk-off
- **TLT** (20+ Year Treasury): Interest rate direction — rising vs falling rates
- **UUP** (US Dollar Index): Dollar strength — strong USD = headwind for multinationals and commodities

#### What Macro Proxies Can Tell You
- Current risk appetite (VIX level vs. 1-year average)
- Rate environment (are bonds rising or falling?)
- Dollar direction (strength or weakness?)

#### What Macro Proxies Cannot Tell You
- **Why** the regime is what it is (causation, not just observation)
- What the Fed will do next meeting (need research, not data)
- Whether the current regime will persist or reverse (need regime analysis, not just current reading)

### Fundamental Screening (via fundamentals_screen.py)

Basic financial metrics for quick valuation assessment.

- **What it provides**: P/E, P/B, P/S, dividend yield, market cap, sector — the standard screening metrics
- **No API key required** — uses yfinance fundamental data
- **Used by**: `scripts/fundamentals_screen.py`
- **Coverage**: Any ticker with yfinance fundamental data (coverage is spotty for small-caps and ADRs)

#### What Fundamental Screening Can Tell You
- Whether a stock is cheap or expensive on basic multiples
- Dividend yield and payout ratio for income investors
- Relative valuation vs. sector peers

#### What Fundamental Screening Cannot Tell You
- **Earnings quality**: Are the earnings real or accounting-driven? (See `scripts/earnings_quality.py`)
- **Capital allocation**: What is management doing with the cash?
- **Competitive position**: Low P/E might mean undervalued — or a value trap
- **Forward trajectory**: Screening is backward-looking; it tells you where the company *was*, not where it's *going*

### Earnings Quality (via earnings_quality.py)

Flags potential earnings manipulation and accounting red flags.

- **What it provides**: Metrics like accruals ratio, quality of earnings, cash flow vs. net income divergence
- **No API key required** — derives from yfinance financial data
- **Used by**: `scripts/earnings_quality.py`

#### What Earnings Quality Can Tell You
- Whether cash flow backs up reported earnings
- Whether accruals are abnormally high (potential manipulation signal)
- Consistency between income statement and cash flow statement

#### What Earnings Quality Cannot Tell You
- **Intent**: High accruals might be manipulation or might be normal business timing
- **Future restatements**: Flags risk, doesn't predict restatements
- **Off-balance-sheet items**: Can't detect what's not in the reported numbers
- **Real economic quality**: A company with clean accounting can still have a deteriorating business

### Short Interest (via short_squeeze.py)

Basic short interest data for assessing bearish positioning.

- **What it provides**: Short interest metrics, days to cover, short squeeze potential indicators
- **No API key required** — uses yfinance or free data sources
- **Used by**: `scripts/short_squeeze.py`

#### What Short Interest Data Can Tell You
- How much of the float is sold short
- Days to cover (short squeeze fuel)
- Whether short interest is rising or falling

#### What Short Interest Data Cannot Tell You
- **Who** is short (smart money vs. retail?)
- **Why** they're short (fundamental bear case vs. hedging)
- **Borrow cost**: How expensive is it to maintain the short position?
- **Real-time changes**: Short interest is reported bi-monthly — it's always stale

---

## Data Quality and Limitations

### The Delay Problem

All free data has a 15-minute delay. For position-trading and investment analysis, this is usually irrelevant. For day-trading or event-driven timing, it's disqualifying.

**When delay matters**:
- Earnings reaction trades (price moves in seconds)
- Fed meeting reactions (entire move in minutes)
- M&A announcements (gap opens, no opportunity to react)
- Breaking news (by the time data reflects it, the move is done)

**When delay doesn't matter**:
- Multi-day/week position trades
- Thesis-driven investments with defined catalysts
- Portfolio allocation decisions
- Risk management and monitoring

### The Survivorship Bias Problem

yfinance only contains currently listed stocks. Delisted stocks (bankruptcies, acquisitions, take-private) are invisible. This means:

- **Backtests overestimate returns**: The stocks you're testing survived; the ones that didn't are excluded
- **Risk is underestimated**: The worst outcomes (bankruptcy, delisting) aren't in your data
- **Sector averages are biased upward**: Only the survivors remain

**The fix**: Be aware of it. Adjust your expectations downward. A 15% backtest return is probably 10-12% after accounting for survivorship bias. A 60% win rate is probably 55%.

### The Quality vs Quantity Problem

More data ≠ better analysis. The question is whether the data resolves your key uncertainty.

- 2 years of daily price data is often MORE useful than 10 years, because the last 2 years reflect the current market structure
- 5 years of quarterly fundamentals tells you more than 20 years, because competitive dynamics change over decades
- One SEC filing read carefully tells you more than 50 price charts scanned quickly

**The fix**: Always ask: "Does this data help me answer my key question?" If not, it's noise. See `references/thesis_first.md` for how to identify what you actually need.

### The Stale Data Problem

Free data sources are not updated in real-time. Fundamental data in particular can be weeks or months old.

| Data Type | Typical Staleness | When It's Dangerous |
|-----------|-------------------|---------------------|
| Price data | 15 minutes | Day-trading, event trading |
| Volume data | 15 minutes | Unusual activity detection |
| Fundamentals (yfinance) | Days to weeks | Earnings season, post-event |
| SEC filings | Days (after filing) | Pre-filing events |
| Macro data | Daily | Rapid regime changes |

**The fix**: Always check *when* the data was last updated. Stale data is not wrong data — it's data about a world that no longer exists. Use web research (see `references/web_research.md`) to supplement with current information.

---

## What's NOT Available (And How to Get It)

These are critical data gaps that scripts cannot fill. You need research and reasoning instead.

### Analyst Consensus and Price Targets

**What's missing**: Consensus EPS estimates, revenue estimates, price targets, analyst ratings distribution.

**How to get it**: Web research — search "[TICKER] analyst consensus" or "[TICKER] EPS estimates 2026". Sources like Yahoo Finance, MarketBeat, and TipRanks provide free summaries.

**Why it matters**: If you're assessing whether a stock is over/under-priced, you need to know what the market *expects*. Price reflects expectations; you need to know what those expectations ARE to determine if they're too high or too low. See `references/what_changes_everything.md`.

### Earnings Call Transcripts

**What's missing**: The actual words management uses on earnings calls — tone, emphasis, what they avoid saying, guidance changes.

**How to get it**: Web research — search "[TICKER] earnings call transcript Q[1-4] [YEAR]". Seeking Alpha, Motley Fool, and company IR pages often have free transcripts.

**Why it matters**: Management tone is one of the most powerful signals in investing. A CEO who sounds uncertain about guidance is more informative than the guidance number itself. See `references/qualitative_mosaic.md`.

### Insider Transaction Data

**What's missing**: Real-time Form 4 filings (insider buys/sells), Section 16 filings, planned 10b5-1 sales.

**How to get it**: Web research — search "[TICKER] insider buying" or "[TICKER] insider transactions". SEC EDGAR has the raw filings; OpenInsider.com aggregates them for free.

**Why it matters**: Insiders sell for many reasons, but they buy for one: they think the stock will go up. Cluster buying by multiple insiders is one of the strongest bullish signals. Cluster selling is a warning. See `references/qualitative_mosaic.md` management section.

### Short Interest and Options Flow

**What's missing**: Short interest (% of float), days to cover, options put/call ratios, unusual options activity.

**How to get it**: Limited free sources — search "[TICKER] short interest" or "[TICKER] short squeeze". Finviz provides some free data. `scripts/short_squeeze.py` provides basic short interest analysis.

**Why it matters**: High short interest can mean either (a) smart money thinks the stock is overpriced or (b) a short squeeze is brewing. The distinction matters enormously. See `references/asset_playbooks.md` special situations section.

### Industry and Competitive Data

**What's missing**: Market share data, industry growth rates, pricing trends, competitive positioning, customer churn.

**How to get it**: Web research — industry reports (often free summaries), trade publications, company investor presentations (on IR pages), SEC filings for competitors (cross-reference).

**Why it matters**: You can't evaluate a company's moat without understanding the competitive landscape. A company growing 15% in a market growing 20% is losing share. The same 15% in a market growing 5% is gaining share. See `references/qualitative_mosaic.md` competitive moat section.

### On-Chain and Crypto-Native Data

**What's missing**: For crypto: holder distribution, exchange flows, active addresses, TVL, staking ratios, token release schedules.

**How to get it**: Web research — Glassnode (limited free tier), Dune Analytics, CoinGlass, TokenUnlocked, DeFiLlama.

**Why it matters**: Crypto price without on-chain context is like equity price without financials — it's just a number. See `references/asset_playbooks.md` crypto section.

---

## Data Source Quick Reference

| Source | Script | Data Type | Delay | Key Limitation |
|--------|--------|-----------|-------|----------------|
| yfinance | `fetch_data.py`, `forecast.py`, `portfolio_optimizer.py` | OHLCV price/volume | 15 min | No fundamentals, no real-time |
| vectorbt YahooData | `backtest.py`, `risk_metrics.py` | OHLCV (backtest-optimized) | 15 min | Same as yfinance |
| SEC EDGAR | `sec_filings.py` | 10-K, 10-Q filings | Days | Backward-looking, no sentiment |
| Macro ETFs | `macro_analysis.py` | VIX, TLT, UUP | 15 min | Proxies only, not direct macro data |
| Sector ETFs | `sector_rotation.py` | Sector momentum/rotation | 15 min | ETF ≠ sector, concentration bias |
| Correlation | `correlation_matrix.py` | Pairwise correlations | 15 min | Historical only, unstable in crises |
| Regime | `regime_detector.py` | Bull/Bear/Sideways detection | 15 min | Lagging indicator, not predictive |
| Short data | `short_squeeze.py` | Short interest basics | Days | Limited depth, delayed |
| Fundamentals | `fundamentals_screen.py` | Basic screening metrics | Days-weeks | Stale, limited coverage |
| Earnings quality | `earnings_quality.py` | Earnings manipulation flags | Days-weeks | Backward-looking only |

---

## Using Data in the Reasoning Loop

Data is not the analysis — it's one input to the reasoning loop. Here's how data fits into the thesis-first process:

1. **Thesis first** (see `references/thesis_first.md`): Form your view based on causal reasoning BEFORE looking at data
2. **Data as test**: Use scripts to check whether the data confirms or denies your thesis
3. **Data as context**: Use macro/sector data to understand the environment your thesis operates in
4. **Data as challenge**: Use data to find the fact that changes your thesis (see `references/what_changes_everything.md`)
5. **Data as sanity check**: Use risk metrics, correlation, and regime data to ensure you're not missing something obvious

**Never**: Run all scripts, then build a thesis from the outputs. That's data mining, not analysis.

**Always**: Know what you're looking for before you look. Then use data to find it — or to prove it wrong.

---

## The Missing-Data Decision Rule

When you can't get the data you need:

| Situation | Action |
|-----------|--------|
| Data exists but not in scripts | Use web research (`references/web_research.md`) |
| Data doesn't exist (proprietary, paywalled) | Acknowledge the gap; reduce conviction accordingly |
| Data is stale | Note staleness; use web research for updates; discount the signal |
| Data contradicts your thesis | This is the most valuable data you've found. Don't ignore it. |
| Data confirms your thesis | Good — but seek disconfirmation before increasing conviction |

**If a critical data gap cannot be resolved, your confidence must be capped at Medium or below.** You cannot have High conviction when a key variable is unknown. See `references/decision_quality.md` for confidence calibration.
