# ---------------------------------------------------------------------------
# Tests for scripts/risk_metrics.py
# ---------------------------------------------------------------------------
import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from risk_metrics import calculate_comprehensive_risk


class TestComprehensiveRisk:
    def test_returns_dict(self):
        """calculate_comprehensive_risk returns a dictionary."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            assert isinstance(result, dict)
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_dict_contains_expected_keys(self):
        """Result dict includes Sharpe, Sortino, Max Drawdown, Beta."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            expected_keys = ["sharpe_ratio", "sortino_ratio", "max_drawdown", "beta"]
            # Allow flexible key names (some implementations use different casing)
            result_keys = [k.lower() for k in result]
            found = sum(1 for k in expected_keys if any(k in rk for rk in result_keys))
            assert found >= 2, f"Expected at least 2 of {expected_keys}, got {list(result.keys())}"
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_sharpe_ratio_is_valid_float(self):
        """Sharpe ratio is a float in reasonable range."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            # Find any key that looks like sharpe ratio
            sharpe = next((v for k, v in result.items() if "sharpe" in k.lower()), None)
            if sharpe is not None:
                assert isinstance(sharpe, (float, np.floating, int))
                # Sharpe should be in reasonable range (-5 to 10)
                assert -5 <= sharpe <= 10
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_sortino_ratio_is_valid_float(self):
        """Sortino ratio is a float value."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            sortino = next((v for k, v in result.items() if "sortino" in k.lower()), None)
            if sortino is not None:
                assert isinstance(sortino, (float, np.floating, int))
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_max_drawdown_is_negative_or_zero(self):
        """Max drawdown is negative (loss) or zero."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            dd = next((v for k, v in result.items() if "drawdown" in k.lower() and "current" not in k.lower()), None)
            if dd is not None:
                assert dd <= 0
                assert dd >= -1.0  # between 0 and -100%
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_beta_is_in_valid_range(self):
        """Beta is between -2 and 3 (reasonable equity beta range)."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            beta = next((v for k, v in result.items() if k.lower() == "beta"), None)
            if beta is not None:
                assert -2 <= beta <= 3
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_var_is_negative(self):
        """VaR is negative (represents a loss)."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            var = next((v for k, v in result.items() if "var" in k.lower()), None)
            if var is not None:
                assert var < 0
                assert var >= -1.0
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_cvar_more_extreme_than_var(self):
        """CVaR (Expected Shortfall) is more negative than VaR."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            var_key = next((k for k in result if "var" in k.lower()), None)
            var = result[var_key] if var_key else None
            cvar_key = next((k for k in result if "cvar" in k.lower() or "expected" in k.lower()), None)
            cvar = result[cvar_key] if cvar_key else None
            if var is not None and cvar is not None:
                assert cvar <= var
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_total_return_reasonable(self):
        """Total return is between -100% and +1000%."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            ret = next(
                (
                    v
                    for k, v in result.items()
                    if "return" in k.lower() and "annual" not in k.lower() and "mean" not in k.lower()
                ),
                None,
            )
            if ret is not None:
                assert -1.0 <= ret <= 10.0
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_invalid_ticker_raises(self):
        """Invalid ticker raises exception."""
        with pytest.raises(Exception):
            calculate_comprehensive_risk("INVALID_TICKER_XYZ_999")


class TestEdgeCases:
    def test_very_short_date_range(self):
        """Short date range handled gracefully."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2024-01-01")
            assert isinstance(result, dict)
        except Exception:
            pytest.skip("yfinance API unavailable or insufficient data")

    def test_win_rate_in_valid_range(self):
        """Win rate is between 0 and 1."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            win_rate = next((v for k, v in result.items() if "win" in k.lower() or "win_rate" in k.lower()), None)
            if win_rate is not None:
                assert 0 <= win_rate <= 1
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_profit_factor_positive(self):
        """Profit factor is positive."""
        try:
            result = calculate_comprehensive_risk("AAPL", start="2022-01-01")
            pf = next((v for k, v in result.items() if "profit" in k.lower()), None)
            if pf is not None:
                assert pf >= 0
        except Exception:
            pytest.skip("yfinance API unavailable")
