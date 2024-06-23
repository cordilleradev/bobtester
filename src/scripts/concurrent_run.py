import datetime
import logging
import concurrent.futures
from tqdm import tqdm
from pandas import DataFrame
import pandas as pd
from logic.backtest import BackTester
from logic.condition import Condition

# BackTester instance
b = BackTester()

# Define the condition for the strategy
condition_long_condor = Condition(
    open_price=158.43,
    period_days=14,
    profit_below_price_factor=0.1,
    profit_above_price_factor=0.1,
    liquidate_below_price_factor=0.2,
    liquidate_above_price_factor=0.2,
)

class CallbackManager:
    def __init__(self, vol: float, fear_and_greed: float) -> None:
        self.vol = vol
        self.fear_and_greed = fear_and_greed

    def callback(self, df: pd.DataFrame) -> bool:
        volatility = df.iloc[-1]['volatility']
        fear = df.iloc[-1]['fear_and_greed']
        return volatility < self.vol and fear < self.fear_and_greed

def backtest_and_return_stats(vol, fear_and_greed):
    manager = CallbackManager(vol, fear_and_greed)
    try:
        response = b.backtest(
            name="googus",
            strategy_conditions=condition_long_condor,
            asset="btc",
            start_position=manager.callback,
            start_from=datetime.date.fromisoformat("2020-01-01")
        )
        stats = response.return_outcome_stats()
        stats['volatility'] = vol
        stats['fear_and_greed'] = fear_and_greed
        return stats
    except Exception as e:
        logging.error(f"Error in backtest vol={vol}, fear_and_greed={fear_and_greed}: {str(e)}")
        return {"error": str(e), "volatility": vol, "fear_and_greed": fear_and_greed}

# Create a list of (vol, fear_and_greed) tuples for the specified ranges
combinations = [(vol, fg) for vol in range(30, 91) for fg in range(30, 101)]

# Execute backtests across different volatility and fear_and_greed indices
outcomes = []
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(backtest_and_return_stats, vol, fg) for vol, fg in combinations]
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
        try:
            result = future.result()
            if "error" not in result:
                outcomes.append(result)
            else:
                logging.error(f"Error in backtest vol={result['volatility']}, fear_and_greed={result['fear_and_greed']}: {result['error']}")
        except Exception as e:
            logging.error(f"Exception while retrieving result: {e}")

# Organize and rank outcomes
df = pd.DataFrame(outcomes)
df['rank'] = df['percent_profitable'].rank(ascending=False)

# Save the DataFrame to a CSV file
df.to_csv('outcomes_ranked.csv', index=False)
