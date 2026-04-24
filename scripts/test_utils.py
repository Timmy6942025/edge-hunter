#!/usr/bin/env python3
"""Unit tests for utils.py shared utility functions."""

import numpy as np
import pandas as pd
import pytest

from utils import extract_price_data, flatten_yf_data, safe_float


# ---------------------------------------------------------------------------
# flatten_yf_data
# ---------------------------------------------------------------------------


class TestFlattenYfData:
    """Tests for flatten_yf_data()."""

    def test_flat_columns_unchanged(self):
        """DataFrame with simple Index columns should pass through unchanged."""
        df = pd.DataFrame({"Close": [1, 2], "Open": [0.5, 1.5]})
        result = flatten_yf_data(df)
        assert list(result.columns) == ["Close", "Open"]
        pd.testing.assert_frame_equal(result, df)

    def test_multiindex_flattened(self):
        """MultiIndex columns should be flattened to level-0 names."""
        arrays = [["Close", "Close", "Open", "Open"], ["AAPL", "MSFT", "AAPL", "MSFT"]]
        index = pd.MultiIndex.from_arrays(arrays)
        df = pd.DataFrame([[1, 2, 0.5, 1.5], [3, 4, 2.5, 3.5]], columns=index)
        result = flatten_yf_data(df)
        assert list(result.columns) == ["Close", "Open"]

    def test_multiindex_deduplication(self):
        """Duplicate columns after flattening should be removed."""
        arrays = [["Close", "Close"], ["AAPL", "MSFT"]]
        index = pd.MultiIndex.from_arrays(arrays)
        df = pd.DataFrame([[1, 2]], columns=index)
        result = flatten_yf_data(df)
        # After flattening, both cols become "Close" → deduplicated to one
        assert list(result.columns) == ["Close"]

    def test_multiindex_does_not_mutate_original(self):
        """flatten_yf_data should not mutate the original DataFrame."""
        arrays = [["Close", "Open"], ["AAPL", "AAPL"]]
        index = pd.MultiIndex.from_arrays(arrays)
        df = pd.DataFrame([[1, 0.5]], columns=index)
        original_cols = df.columns.copy()
        _ = flatten_yf_data(df)
        pd.testing.assert_index_equal(df.columns, original_cols)

    def test_empty_dataframe(self):
        """Empty DataFrame with simple columns should pass through."""
        df = pd.DataFrame(columns=["Close", "Open"])
        result = flatten_yf_data(df)
        assert list(result.columns) == ["Close", "Open"]


# ---------------------------------------------------------------------------
# extract_price_data
# ---------------------------------------------------------------------------


class TestExtractPriceData:
    """Tests for extract_price_data()."""

    def test_flat_single_ticker_close(self):
        """Flat DataFrame with Close column → returns Close Series."""
        df = pd.DataFrame({"Close": [10, 20, 30], "Open": [9, 19, 29]})
        result = extract_price_data(df, "Close")
        pd.testing.assert_series_equal(result, df["Close"])

    def test_flat_single_ticker_adj_close_fallback(self):
        """If Close missing but Adj Close present, should fall back."""
        df = pd.DataFrame({"Adj Close": [10, 20, 30], "Open": [9, 19, 29]})
        result = extract_price_data(df, "Close")
        pd.testing.assert_series_equal(result, df["Adj Close"])

    def test_flat_missing_column_returns_first(self):
        """If requested column and Adj Close both missing, returns first column."""
        df = pd.DataFrame({"High": [15, 25, 35], "Low": [5, 15, 25]})
        result = extract_price_data(df, "Close")
        pd.testing.assert_series_equal(result, df["High"])

    def test_multiindex_single_ticker(self):
        """MultiIndex from single-ticker yfinance download returns DataFrame."""
        arrays = [["Close", "Open"], ["AAPL", "AAPL"]]
        index = pd.MultiIndex.from_arrays(arrays)
        df = pd.DataFrame([[10, 9], [20, 19], [30, 29]], columns=index)
        result = extract_price_data(df, "Close")
        # raw[column] on MultiIndex returns DataFrame with ticker columns
        assert isinstance(result, pd.DataFrame)
        assert "AAPL" in result.columns
        assert list(result["AAPL"]) == [10, 20, 30]

    def test_multiindex_multi_ticker(self):
        """MultiIndex from multi-ticker yfinance download returns DataFrame."""
        arrays = [["Close", "Close", "Open", "Open"], ["AAPL", "MSFT", "AAPL", "MSFT"]]
        index = pd.MultiIndex.from_arrays(arrays)
        df = pd.DataFrame([[10, 40, 9, 39], [20, 50, 19, 49]], columns=index)
        result = extract_price_data(df, "Close")
        # Should return a DataFrame with tickers as columns
        assert isinstance(result, pd.DataFrame)
        assert "AAPL" in result.columns
        assert "MSFT" in result.columns

    def test_multiindex_adj_close_fallback(self):
        """MultiIndex with Adj Close but no Close falls back to Adj Close."""
        arrays = [["Adj Close", "Open"], ["AAPL", "AAPL"]]
        index = pd.MultiIndex.from_arrays(arrays)
        df = pd.DataFrame([[10, 9], [20, 19]], columns=index)
        result = extract_price_data(df, "Close")
        # raw["Adj Close"] on MultiIndex returns DataFrame with ticker columns
        assert isinstance(result, pd.DataFrame)
        assert "AAPL" in result.columns
        assert list(result["AAPL"]) == [10, 20]

    def test_multiindex_missing_price_type(self):
        """If requested price type doesn't exist, returns first available."""
        arrays = [["High", "Low"], ["AAPL", "AAPL"]]
        index = pd.MultiIndex.from_arrays(arrays)
        df = pd.DataFrame([[15, 5], [25, 15]], columns=index)
        result = extract_price_data(df, "Close")
        # Falls back to first column
        assert len(result) == 2

    def test_custom_column(self):
        """Can request Open, High, Low, etc."""
        df = pd.DataFrame({"Open": [9, 19, 29], "Close": [10, 20, 30]})
        result = extract_price_data(df, "Open")
        pd.testing.assert_series_equal(result, df["Open"])


# ---------------------------------------------------------------------------
# safe_float
# ---------------------------------------------------------------------------


class TestSafeFloat:
    """Tests for safe_float()."""

    def test_integer(self):
        assert safe_float(42) == 42.0

    def test_float(self):
        assert safe_float(3.14) == pytest.approx(3.14)

    def test_string_number(self):
        assert safe_float("7.5") == 7.5

    def test_none_returns_default(self):
        assert safe_float(None) == 0.0

    def test_none_custom_default(self):
        assert safe_float(None, default=-1.0) == -1.0

    def test_nan_returns_default(self):
        assert safe_float(float("nan")) == 0.0

    def test_inf_returns_default(self):
        assert safe_float(float("inf")) == 0.0

    def test_neg_inf_returns_default(self):
        assert safe_float(float("-inf")) == 0.0

    def test_unconvertible_string(self):
        assert safe_float("not_a_number") == 0.0

    def test_unconvertible_string_custom_default(self):
        assert safe_float("not_a_number", default=99.0) == 99.0

    def test_pandas_series(self):
        s = pd.Series([10.5, 20.5])
        assert safe_float(s) == 10.5

    def test_pandas_series_single_element(self):
        s = pd.Series([42.0])
        assert safe_float(s) == 42.0

    def test_pandas_series_empty(self):
        s = pd.Series([], dtype=float)
        assert safe_float(s) == 0.0

    def test_pandas_series_empty_custom_default(self):
        s = pd.Series([], dtype=float)
        assert safe_float(s, default=-99.0) == -99.0

    def test_numpy_scalar(self):
        assert safe_float(np.float64(3.14)) == pytest.approx(3.14)

    def test_numpy_int(self):
        assert safe_float(np.int64(7)) == 7.0

    def test_boolean(self):
        assert safe_float(True) == 1.0
        assert safe_float(False) == 0.0

    def test_list_raises_no_crash(self):
        """Lists are not directly convertible — should return default."""
        assert safe_float([1, 2, 3]) == 0.0

    def test_dict_raises_no_crash(self):
        """Dicts are not directly convertible — should return default."""
        assert safe_float({"a": 1}) == 0.0

    def test_zero(self):
        assert safe_float(0) == 0.0

    def test_negative(self):
        assert safe_float(-5.5) == -5.5
