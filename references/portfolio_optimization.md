# Portfolio Optimization

> **Role in this skill**: Appendix — implementation details for portfolio optimization strategies. These are tools to test a thesis about asset allocation, not the starting point. Form your portfolio thesis first (see `references/thesis_first.md` and `references/asset_playbooks.md`), then use these methods to optimize. For when to concentrate vs diversify, see `references/decision_quality.md`.

---

## The Concentration vs Diversification Decision

Before running ANY optimizer, answer this: **Should this portfolio be concentrated or diversified?**

The optimizer will always give you an answer. But the right *structure* of the portfolio is a reasoning decision, not an optimization output.

### When to Concentrate (5-8 positions)

| Condition | Why |
|-----------|-----|
| You have high-conviction theses on specific assets | Edge is in the thesis, not the portfolio math |
| The assets are uncorrelated or negatively correlated | Concentration with low correlation = free diversification |
| You can define what would make you wrong on each position | Risk is knowable and manageable |
| The market is in a regime where selectivity matters | Bear markets reward stock-pickers; bull markets reward indexers |
| You're operating in your circle of competence | You know these assets deeply enough to size with conviction |

**The Druckenmiller principle**: "I've made all my money from 5-6 positions. All my losses from the other 30." Concentration works when your thesis is genuinely differentiated. It destroys you when your thesis is the same as everyone else's and you're just levered.

### When to Diversify (15-30+ positions)

| Condition | Why |
|-----------|-----|
| You don't have strong conviction on individual positions | Diversification is the rational response to uncertainty |
| The theses are correlated (same sector, same driver) | Concentration just magnifies the same bet |
| You're indexing or tracking a benchmark | The job is to match the market, not beat it |
| The regime is uncertain and you have no edge | When you don't know, don't pretend you do |
| Position sizing discipline is weak | Diversification is a guardrail against overconfidence |

**The Bogle principle**: "Don't look for the needle. Buy the haystack." Diversification works when you don't have an edge on any individual position. It's the correct default for most investors most of the time.

### The Meta-Point

Most investors are diversified when they should be concentrated (they have a real edge but are too scared to bet) and concentrated when they should be diversified (they have one thesis but are overconfident in it).

**The fix**: Size your positions to your conviction quality, not to your comfort level. See `references/decision_quality.md` for confidence calibration.

---

## Optimization Methods

### Max Sharpe Ratio

Optimize portfolio to maximize risk-adjusted return.

- Implemented in `scripts/portfolio_optimizer.py` using PyPortfolioOpt
- Best for: Long-term allocation where you believe the mean-variance framework captures reality
- Danger: Maximizes Sharpe on *historical* data. The future correlation and return structure will be different. The "optimal" portfolio is often the most fragile.

### Min Volatility

Optimize for lowest volatility at a target return.

- Modify `scripts/portfolio_optimizer.py` to use `ef.min_volatility()`
- Best for: Capital preservation mandates, risk-sensitive investors, bear market positioning
- Danger: Min-vol portfolios load up on low-vol assets that may be crowded. When the crowded trade unwinds, min-vol can become max-loss.

### Equal Weight

Simple allocation: equal weight to all assets.

- No optimization needed, just divide 1 by number of tickers
- Best for: When you don't trust historical return estimates (which is most of the time), when you want to avoid optimizer bias
- Danger: Treats all positions as equal regardless of conviction, quality, or risk. Sensible default, but not optimal if you have genuine information.

### Risk Parity (Inverse Volatility)

Weight positions inversely to their volatility — equal risk contribution from each position.

- Implemented in `scripts/portfolio_optimizer.py` as risk parity mode
- Best for: When you want to avoid any single position dominating portfolio risk, when you have mixed asset types with very different volatilities
- Danger: Leverages low-vol assets to match risk contribution. This leverage is implicit and often unrecognized. In a crisis, correlations go to 1 and the risk parity benefit vanishes.

### Efficient Frontier

Set of portfolios with maximum return for a given risk level.

- Use `ef.efficient_frontier()` to generate points
- Best for: Understanding the trade-off landscape, not for selecting a specific portfolio
- Danger: The frontier is drawn from historical data. The *future* frontier will look different. Use it for intuition, not prescription.

---

## When Optimization Fails

Portfolio optimization is not a magic bullet. It fails in specific, predictable ways.

### 1. Garbage In, Garbage Out

The optimizer requires expected returns and a covariance matrix. Both are estimated from historical data. If your inputs are wrong, the "optimal" portfolio is precisely wrong — not just random, but systematically tilted toward the worst possible allocation.

**The fix**: Use equal weight or risk parity when you don't have strong return forecasts. Only optimize when you have a genuine thesis about relative returns.

### 2. Correlation Breakdown in Crises

The covariance matrix is estimated from normal periods. In a crisis, correlations spike toward 1.0. The diversification you thought you had evaporates exactly when you need it most.

**The fix**: Stress-test your portfolio under crisis correlations (assume all equities at 0.8+ correlation). If the drawdown is unacceptable, you're not as diversified as you think. Use `scripts/correlation_matrix.py` to see current correlations, then imagine them 2-3x higher.

### 3. Regime Sensitivity

The "optimal" portfolio in a bull market is very different from the optimal portfolio in a bear market. Optimizing over a period that includes both gives you an average that's optimal for neither.

**The fix**: Run optimization separately for different regimes (see `scripts/regime_detector.py`). A portfolio that's robust across regimes is better than one that's theoretically optimal in one regime.

### 4. Overfitting to Recent Data

If you optimize over 1-2 years of data, you're fitting to a specific regime. If you optimize over 10+ years, the early data is irrelevant to current market structure.

**The fix**: Use 3-5 years as the primary window, but check robustness across multiple windows. If the "optimal" allocation changes dramatically with the window, it's not robust — it's overfit.

### 5. Turnover and Transaction Costs

Rebalancing to the "optimal" portfolio every month generates transaction costs that can easily exceed the supposed optimization benefit.

**The fix**: Only rebalance when a position drifts more than 5-10% from target weight, or when your thesis changes. Don't rebalance just because the optimizer says the weights shifted.

---

## Position Sizing: The Kelly Criterion

Position sizing is more important than portfolio optimization. The optimizer tells you *relative* weights; Kelly tells you *absolute* size.

### What Kelly Does

The Kelly Criterion calculates the fraction of your bankroll to bet to maximize long-term geometric growth:

```
f* = (p * b - q) / b
```

Where:
- `p` = probability of winning (win rate from backtest)
- `q` = probability of losing (1 - p)
- `b` = win/loss ratio (average win ÷ average loss)

- Implemented in `scripts/kelly_sizer.py` (uses outputs from `scripts/backtest.py` and `scripts/risk_metrics.py`)
- Returns full Kelly and half-Kelly fractions

### Kelly Rules

| Rule | Why |
|------|-----|
| **Never use full Kelly** | Full Kelly maximizes growth but with terrifying drawdowns (30-50%+) |
| **Use half-Kelly as default** | Half-Kelly captures ~75% of the growth with ~50% of the variance |
| **Reduce Kelly further when uncertain** | If your win rate and payoff ratio are estimated (they always are), the true Kelly is lower |
| **Kelly assumes independent bets** | Correlated positions make Kelly overestimate optimal size |
| **Kelly doesn't know about black swans** | It assumes the distribution is known. It isn't. Always size below Kelly. |

### Position Sizing Decision Tree

```
Do you have a quantified edge? (Backtested win rate + payoff ratio)
├── YES → Use half-Kelly as starting point
│         Are the estimates reliable? (>100 trades, robust across regimes)
│         ├── YES → Size at half-Kelly
│         └── NO  → Size at quarter-Kelly (or less)
├── NO (qualitative thesis only) → Use confidence-calibrated sizing
│         High conviction (survived red-team): 5-8% of portfolio
│         Medium conviction: 2-4% of portfolio
│         Low conviction: 1-2% or skip
└── NO EDGE → 0% — Pass
```

See `references/decision_quality.md` for the full confidence calibration framework.

---

## Correlation Awareness

Correlation is the most misunderstood input in portfolio construction.

### What Correlation Tells You

- How two assets have moved *relative to their own means* historically
- A starting point for understanding diversification potential

### What Correlation Does NOT Tell You

- What will happen in the future (correlations are unstable)
- What will happen in a crisis (correlations spike to 1.0 when you need diversification most)
- Whether two assets share a causal driver (spurious correlation is everywhere)
- How to construct a portfolio (low correlation ≠ good diversification if tail risk is correlated)

### Using `scripts/correlation_matrix.py`

Run it to understand the *current* correlation structure. But then:

1. **Stress test**: What happens if all correlations move to 0.7+?
2. **Check rolling correlation**: Is the correlation stable or does it change with regime?
3. **Identify causal overlap**: Do these assets share a driver? If yes, the correlation may be more stable than it looks — and the diversification may be illusory.

### The Diversification Paradox

The best diversification comes from assets that are:
- **Fundamentally different** (different drivers, different sectors, different geographies)
- **Currently uncorrelated** (low historical correlation)
- **Not both dependent on the same tail risk** (e.g., stocks and corporate bonds both crash in recessions)

If your portfolio is "diversified" across 20 tech stocks, you have 20 positions but 1 bet.

---

## Regime-Aware Portfolio Construction

Different regimes demand different portfolio structures. Optimizing without knowing the regime is like dressing without knowing the weather.

| Regime | Optimal Structure | Key Risk | Scripts to Run |
|--------|-------------------|----------|-----------------|
| **Bull** | Concentrated in momentum/growth leaders | Crowding, multiple expansion reversal | `regime_detector.py`, `sector_rotation.py` |
| **Bear** | Diversified, defensive, cash-heavy | Drawdown magnitude, duration | `regime_detector.py`, `risk_metrics.py` |
| **Sideways/Chop** | Equal weight or risk parity | Whipsaw, mean-reversion traps | `correlation_matrix.py`, `regime_detector.py` |
| **Transition** | Reducing risk, raising cash | Regime misidentification | `macro_analysis.py`, `regime_detector.py` |

**The meta-rule**: If you're unsure what regime you're in, you're in a transition. Act accordingly (less risk, more cash, wider stops).

Use `scripts/regime_detector.py` to identify the current regime, then construct the portfolio type appropriate for that regime — don't just run the optimizer and assume the output is universally valid.

---

## The Portfolio Construction Checklist

Before finalizing any portfolio:

- [ ] Have I decided whether to concentrate or diversify based on my conviction quality?
- [ ] Have I run the optimizer appropriate for the current regime?
- [ ] Have I stress-tested the portfolio under crisis correlations (0.7+)?
- [ ] Have I sized positions using Kelly or confidence-calibrated sizing?
- [ ] Have I checked for hidden concentration (same driver across positions)?
- [ ] Do I have rebalancing rules that don't rely on daily optimization?
- [ ] Would I be comfortable with a 30% drawdown on this portfolio?
- [ ] Is the portfolio robust to regime change, or is it optimal for one regime only?

**If you can't check all boxes, the portfolio isn't ready.** See `references/decision_quality.md` for the full decision hygiene framework.
