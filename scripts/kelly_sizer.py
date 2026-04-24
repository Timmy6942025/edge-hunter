#!/usr/bin/env python3
"""
Kelly Criterion Position Sizer
Calculates optimal position size based on win rate and win/loss ratio
"""
import argparse
import sys

def calculate_kelly(win_rate, avg_win_pct, avg_loss_pct):
    """
    Kelly Criterion: f* = (p*b - q) / b
    where:
    p = win rate (0-1)
    b = win/loss ratio (avg_win / abs(avg_loss))
    q = 1 - p = loss rate
    """
    if avg_loss_pct == 0:
        return 0

    p = win_rate
    q = 1 - p
    b = abs(avg_win_pct / avg_loss_pct)

    kelly = (p * b - q) / b

    # Kelly Fraction (most use half-Kelly for safety)
    half_kelly = kelly * 0.5

    return {
        'full_kelly': kelly * 100,  # as percentage
        'half_kelly': half_kelly * 100,
        'win_rate': win_rate * 100,
        'win_loss_ratio': b
    }

def get_strategy_stats(ticker):
    """Extract stats from backtest.py output (simplified)"""
    import subprocess
    import re

    try:
        result = subprocess.run(
            [sys.executable, "backtest.py", ticker],
            capture_output=True, text=True, cwd=".", timeout=120,
            check=False
        )
        output = result.stdout

        # Extract win rate (simplified - count WIN vs LOSS)
        win_count = output.count("WIN")
        loss_count = output.count("LOSS")
        total = win_count + loss_count

        if total == 0:
            return None

        win_rate = win_count / total

        # Extract avg win/loss from risk_metrics.py
        result2 = subprocess.run(
            [sys.executable, "risk_metrics.py", ticker],
            capture_output=True, text=True, cwd=".", timeout=120,
            check=False
        )
        output2 = result2.stdout

        # Parse avg win/loss
        avg_win_match = re.search(r'Avg Win: ([\d.-]+)%', output2)
        avg_loss_match = re.search(r'Avg Loss: ([\d.-]+)%', output2)

        if avg_win_match and avg_loss_match:
            avg_win = float(avg_win_match.group(1))
            avg_loss = float(avg_loss_match.group(1))
            return {
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss
            }
    except Exception as e:
        print(f"Error getting stats: {e}")

    return None

def suggest_position_size(ticker, account_size=100000):
    """Suggest position size based on Kelly Criterion"""
    print(f"\n{'='*70}")
    print(f"KELLY CRITERION POSITION SIZING: {ticker}")
    print(f"{'='*70}")

    stats = get_strategy_stats(ticker)

    if not stats:
        print(f"\nUsing default assumptions for {ticker}:")
        print(f"  (Run backtest.py and risk_metrics.py first for accurate numbers)\n")
        # Default assumptions
        stats = {
            'win_rate': 0.55,
            'avg_win': 2.5,
            'avg_loss': -1.5
        }

    win_rate = stats['win_rate']
    avg_win = stats['avg_win']
    avg_loss = stats['avg_loss']

    kelly = calculate_kelly(win_rate, avg_win, avg_loss)

    print(f"\nSTRATEGY STATISTICS:")
    print(f"  Win Rate: {win_rate*100:.1f}%")
    print(f"  Average Win: {avg_win:.2f}%")
    print(f"  Average Loss: {avg_loss:.2f}%")
    print(f"  Win/Loss Ratio: {kelly['win_loss_ratio']:.2f}")

    print(f"\nKELLY CRITERION RESULTS:")
    print(f"  Full Kelly: {kelly['full_kelly']:.1f}% of portfolio")
    print(f"  Half Kelly (Recommended): {kelly['half_kelly']:.1f}% of portfolio")

    # Position sizes
    sizes = {
        'Conservative (1/4 Kelly)': kelly['full_kelly'] * 0.25,
        'Moderate (1/2 Kelly)': kelly['half_kelly'],
        'Aggressive (Full Kelly)': kelly['full_kelly'],
    }

    print(f"\nPOSITION SIZE RECOMMENDATIONS (Account: ${account_size:,.0f}):")
    print(f"\n{'Strategy':<30} {'Pct':>10} {'Amount':>15}")
    print(f"{'-'*70}")

    for name, size_pct in sizes.items():
        display_pct = max(size_pct, 0)
        amount = account_size * (display_pct / 100)
        print(f"{name:<30} {display_pct:>9.1f}% ${amount:>14,.0f}")

    # Risk warnings
    print(f"\n{'='*70}")
    print(f"RISK WARNINGS:")
    if kelly['full_kelly'] > 25:
        print(f"  ⚠ Full Kelly >25% - VERY AGGRESSIVE, high ruin risk")
    if kelly['full_kelly'] < 0:
        print(f"  ⚠ Negative Kelly - Strategy has negative expectancy, DO NOT TRADE")
    if win_rate < 0.4:
        print(f"  ⚠ Win rate <40% - Consider improving strategy")
    if kelly['win_loss_ratio'] < 1.5:
        print(f"  ⚠ Win/Loss ratio <1.5 - Need bigger wins or smaller losses")

    print(f"\nTIP: Most professionals use Half Kelly or less to reduce ruin risk")
    print(f"{'='*70}\n")

    return kelly

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kelly Criterion position sizing")
    parser.add_argument("ticker", help="Stock ticker (e.g., AAPL)")
    parser.add_argument("--account", type=float, default=100000, help="Account size (default: $100,000)")
    args = parser.parse_args()
    suggest_position_size(args.ticker, args.account)

