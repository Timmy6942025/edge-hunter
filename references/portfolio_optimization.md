# Portfolio Optimization

> **Role in this skill**: Appendix — implementation details for portfolio optimization strategies. These are tools to test a thesis about asset allocation, not the starting point. Form your portfolio thesis first (see `references/thesis_first.md` and `references/asset_playbooks.md`), then use these methods to optimize. For when to concentrate vs diversify, see `references/decision_quality.md`.

## Max Sharpe Ratio
Optimize portfolio to maximize risk-adjusted return
- Implemented in `scripts/portfolio_optim.py` using PyPortfolioOpt

## Min Volatility
Optimize for lowest volatility at a target return
- Modify `scripts/portfolio_optim.py` to use `ef.min_volatility()`

## Equal Weight
Simple allocation: equal weight to all assets
- No optimization needed, just divide 1 by number of tickers

## Efficient Frontier
Set of portfolios with maximum return for a given risk level
- Use `ef.efficient_frontier()` to generate points
