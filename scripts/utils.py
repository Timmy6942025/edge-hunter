#!/usr/bin/env python3
"""
Shared Utility Functions for Professional Quant Scripts
=========================================================
Common helpers used across all analysis scripts.
"""

import pandas as pd
import numpy as np


def flatten_yf_data(data):
    """Flatten MultiIndex columns from yfinance download.

    Newer yfinance returns MultiIndex DataFrames even for single tickers.
    This function flattens them to simple column names.

    Args:
        data: pandas DataFrame from yf.download()

    Returns:
        Flattened DataFrame with simple column names
    """
    if isinstance(data.columns, pd.MultiIndex):
        data = data.copy()
        data.columns = data.columns.get_level_values(0)
        data = data.loc[:, ~data.columns.duplicated()]
    return data


def extract_price_data(raw, column='Close'):
    """Extract price data from yfinance download result.

    Handles both single-ticker and multi-ticker downloads.
    Returns a DataFrame with ticker names as columns.

    Args:
        raw: DataFrame from yf.download()
        column: Price column to extract ('Close', 'Adj Close', 'Open', etc.)

    Returns:
        DataFrame with tickers as columns, or Series for single ticker
    """
    if isinstance(raw.columns, pd.MultiIndex):
        # MultiIndex: columns are (PriceType, Ticker)
        price_types = raw.columns.get_level_values(0).unique()
        if column in price_types:
            data = raw[column]
        elif 'Adj Close' in price_types and column == 'Close':
            data = raw['Adj Close']
        else:
            data = raw.iloc[:, 0]
    else:
        # Flat columns - single ticker
        if column in raw.columns:
            data = raw[column]
        elif 'Adj Close' in raw.columns and column == 'Close':
            data = raw['Adj Close']
        else:
            data = raw.iloc[:, 0]

    # Ensure proper column names if DataFrame
    if isinstance(data, pd.DataFrame) and isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(-1)

    return data


def safe_float(value, default=0.0):
    """Safely convert a value to float.

    Handles pandas Series (takes first value), None, NaN, etc.

    Args:
        value: Value to convert (can be scalar, Series, None, etc.)
        default: Default value if conversion fails

    Returns:
        float value
    """
    try:
        if value is None:
            return default
        if isinstance(value, pd.Series):
            value = value.iloc[0] if len(value) > 0 else default
        result = float(value)
        if np.isnan(result) or np.isinf(result):
            return default
        return result
    except (ValueError, TypeError, IndexError):
        return default
