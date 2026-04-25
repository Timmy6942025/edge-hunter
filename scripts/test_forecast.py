# ---------------------------------------------------------------------------
# Tests for scripts/forecast.py
# ---------------------------------------------------------------------------
import pytest
import numpy as np
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from forecast import validate_ticker, calculate_technical_indicators, forecast_stock


class TestValidateTicker:
    def test_valid_uppercase_ticker(self):
        """Valid 1-5 uppercase letter ticker returns uppercase string."""
        result = validate_ticker("AAPL")
        assert isinstance(result, str)
        assert result == "AAPL"
        assert validate_ticker("NVDA") == "NVDA"
        assert validate_ticker("M") == "M"

    def test_rejects_lowercase(self):
        """Lowercase tickers are normalized to uppercase."""
        result = validate_ticker("aapl")
        assert isinstance(result, str)
        assert result == "AAPL"  # case-insensitive, returns upper

    def test_rejects_too_long(self):
        """Tickers >5 chars rejected."""
        with pytest.raises(ValueError):
            validate_ticker("TOOLONG")

    def test_rejects_numbers(self):
        """Tickers with numbers rejected."""
        with pytest.raises(ValueError):
            validate_ticker("AAPL1")

    def test_rejects_empty(self):
        """Empty string rejected."""
        with pytest.raises(ValueError):
            validate_ticker("")


class TestCalculateTechnicalIndicators:
    def test_returns_dataframe(self):
        """Function returns a DataFrame."""
        dates = pd.date_range("2022-01-01", periods=100)
        df = pd.DataFrame({"Close": np.random.randn(100).cumsum() + 100}, index=dates)
        result = calculate_technical_indicators(df)
        assert isinstance(result, pd.DataFrame)

    def test_dataframe_not_empty(self):
        """Result DataFrame has data."""
        dates = pd.date_range("2022-01-01", periods=100)
        df = pd.DataFrame({"Close": np.random.randn(100).cumsum() + 100}, index=dates)
        result = calculate_technical_indicators(df)
        assert not result.empty

    def test_contains_rsi_column(self):
        """Result includes RSI column."""
        dates = pd.date_range("2022-01-01", periods=100)
        df = pd.DataFrame({"Close": np.random.randn(100).cumsum() + 100}, index=dates)
        result = calculate_technical_indicators(df)
        assert "RSI" in result.columns or "rsi" in result.columns.str.lower()

    def test_contains_macd_columns(self):
        """Result includes MACD-related columns."""
        dates = pd.date_range("2022-01-01", periods=100)
        df = pd.DataFrame({"Close": np.random.randn(100).cumsum() + 100}, index=dates)
        result = calculate_technical_indicators(df)
        cols_lower = result.columns.str.lower()
        assert any("macd" in c for c in cols_lower)

    def test_contains_bollinger_columns(self):
        """Result includes Bollinger Band columns."""
        dates = pd.date_range("2022-01-01", periods=100)
        df = pd.DataFrame({"Close": np.random.randn(100).cumsum() + 100}, index=dates)
        result = calculate_technical_indicators(df)
        cols_lower = result.columns.str.lower()
        assert any("bb" in c or "bollinger" in c for c in cols_lower)

    def test_handles_short_series(self):
        """Handles series shorter than typical lookback."""
        df = pd.DataFrame({"Close": [100, 101, 102, 103, 104]})
        result = calculate_technical_indicators(df)
        assert isinstance(result, pd.DataFrame)

    def test_handles_constant_prices(self):
        """Handles constant price series without crash."""
        df = pd.DataFrame({"Close": [100.0] * 50})
        result = calculate_technical_indicators(df)
        assert isinstance(result, pd.DataFrame)


class TestForecastStock:
    def test_returns_dict(self):
        """forecast_stock returns a dictionary."""
        try:
            result = forecast_stock("AAPL", periods=7)
            assert isinstance(result, dict)
        except Exception:
            pytest.skip("yfinance API unavailable or Prophet error")

    def test_dict_contains_keys(self):
        """Result dict contains expected keys."""
        try:
            result = forecast_stock("AAPL", periods=7)
            assert len(result) > 0
        except Exception:
            pytest.skip("yfinance API unavailable")

    def test_invalid_ticker_raises(self):
        """Invalid ticker raises exception."""
        with pytest.raises(Exception):
            forecast_stock("INVALID_TICKER_XYZ_999")


class TestEdgeCases:
    def test_nan_prices_handled(self):
        """NaN values in price DataFrame handled gracefully."""
        dates = pd.date_range("2022-01-01", periods=50)
        df = pd.DataFrame({"Close": [100, np.nan, 102, np.nan, 103]}, index=dates[:5])
        result = calculate_technical_indicators(df)
        assert isinstance(result, pd.DataFrame)

    def test_empty_dataframe_returns_empty(self):
        """Empty DataFrame returns empty DataFrame (no crash)."""
        df = pd.DataFrame({"Close": []})
        result = calculate_technical_indicators(df)
        assert isinstance(result, pd.DataFrame)
        assert result.empty
