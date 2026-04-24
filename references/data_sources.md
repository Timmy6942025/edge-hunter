# Free Data Sources (No API Key)

> **Role in this skill**: Appendix — reference for what data is available and its limitations. Data is an input, not the analysis. For how to find information beyond what these sources provide (qualitative research, primary sources, etc.), see `references/research_for_edge.md`.

## yfinance
- Fetch historical stock data from Yahoo Finance
- No API key required
- Used in `scripts/fetch_data.py`, `scripts/forecast.py`, `scripts/portfolio_optim.py`

## vectorbt YahooData
- Built-in data downloader via yfinance
- No API key required
- Used in `scripts/backtest.py`, `scripts/risk_metrics.py`

## Notes
- All data is delayed by 15 minutes for free yfinance access
- For real-time data, paid APIs are required (not supported in this skill)
