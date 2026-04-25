# Changelog

All notable changes to the edge-hunter skill are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-04-17

### Added
- New script: `earnings_transcript.py` — fetches and analyzes earnings call transcripts with management tone scoring
- New script: `macro_forecast.py` — generates 3/6-month directional forecasts across rates, gold, oil, dollar, equities  
- New script: `short_squeeze.py` — enhanced with gamma exposure analysis, squeeze probability scoring, and sector comparison
- New reference: `earnings_analysis.md` — how to extract investment edge from earnings calls, Q&A red flags, manipulation signals
- New reference: `cycle_analysis.md` — market cycle identification across asset classes, cycle interactions, when cycles break
- New test file: `test_forecast.py` — coverage for forecast.py RSI/MACD/Prophet/signal generation
- New test file: `test_risk_metrics.py` — coverage for Sharpe/Sortino/MDD/Beta/VaR calculations
- New test file: `test_macro_analysis.py` — coverage for macro regime detection and VIX/TLT/UUP fetching
- New file: `requirements.txt` — pinned, tested dependency versions for reproducible installation

### Changed
- Skill renamed from `deep-market-analysis` to `edge-hunter` — accurate naming reflecting thesis-driven reasoning over script orchestration
- README rewritten with quick-start example showing actual output format for a real ticker
- SKILL.md expanded with "What good looks like" example output section
- SKILL.md expanded with "Common failure modes" section  
- SKILL.md output format standardized: one-sentence thesis lead + probability-weighted risk profile required in every analysis
- All internal references updated from `deep-market-analysis` to `edge-hunter` across README, SKILL.md, scripts, and config files

### Fixed
- Improved short_squeeze.py data sourcing with gamma exposure analysis

## [2.1.0] - 2026-04-17

### Changed
- Skill renamed from `professional-quant` to `deep-market-analysis` — accurate naming reflecting reasoning-first paradigm

## [2.0.0] - 2026-04-17

### Added
- 9-step reasoning loop: Orient → Build thesis → Identify unknowns → Targeted research → Test with scripts → Red-team → Reconcile → Decide → Set monitoring triggers
- 7 new reference files: thesis_first, self_verification, qualitative_mosaic, asset_playbooks, research_for_edge, decision_quality, what_changes_everything
- 5 rewritten reference files: deep_analysis, deep_thought_template, web_research, advanced_techniques, model_pitfalls
- 2 enriched reference files: portfolio_optimization, data_sources

### Changed
- Transformed from script-orchestration-first to thesis-driven deep market intelligence
- README completely rewritten from script-focused to reasoning-first
- 56 tests added

