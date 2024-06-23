
# Cryptocurrency Trading Strategy Backtester

## Overview
This package provides a comprehensive toolkit for backtesting cryptocurrency trading strategies. It allows users to define specific trading conditions, execute backtests in parallel, and visualize the outcomes with detailed graphical representations.

## Modules
- **Backtest**: Simulates trading strategies and evaluates their performance.
- **Condition**: Sets the rules for when trades should be initiated and closed.
- **Manipulate**: Preprocesses data for analysis.
- **Normalize**: Scales and normalizes financial data.
- **Concurrent Run**: Utilizes multi-threading to run multiple simulations simultaneously.
- **Plot**: Generates plots to visualize trading data and strategy performance.

## Examples

**Running a Backtest**
```python
from backtest import BackTester
from condition import Condition

# Define trading conditions
condition = Condition(open_price=0, period_days=14, profit_below_price_factor=0.1, profit_above_price_factor=0.1)
backtester = BackTester()

# Run backtest from a specific start date
result = backtester.backtest("SampleStrategy", condition, "btc", lambda data: data['close'][-1] > data['open'][-1], start_from="2020-01-01")
print(result.return_outcomes())
```
