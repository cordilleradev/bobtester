import datetime
from typing import List, Tuple, Dict, Callable
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
from pandas import DataFrame, Index
from bobtester.condition import Condition
from bobtester import Outcomes
from bobtester.normalize import CryptoDataMerger
from bobtester.manipulate import get_sub_frames
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

pd.options.mode.chained_assignment = None  # default='warn'

class BackTestResult:
    def __init__(self, name: str, outcomes: pd.DataFrame, crypto_data: pd.DataFrame):
        self.name = name
        self.outcomes = outcomes
        self.crypto_data = crypto_data
        self.prepare_data()

    def prepare_data(self):
        # Initialize the outcome column in crypto_data
        self.crypto_data['outcome'] = 'SKIPPED'

        # Assign outcomes to the crypto_data based on the dates in the outcomes DataFrame
        for index, row in self.outcomes.iterrows():
            mask = (self.crypto_data['date'] >= row['start_date']) & (self.crypto_data['date'] <= row['end_date'])
            self.crypto_data.loc[mask, 'outcome'] = row['outcome']

    def export_outcome(self, merged_crypto_data_path : str | None = None, outcome_data_path : str | None = None):
        if outcome_data_path is not None:
            self.outcomes.to_csv(outcome_data_path)
        if merged_crypto_data_path is not None:
            self.crypto_data.to_csv(merged_crypto_data_path)

    def return_outcome_stats(self) -> Dict[str, float]:
        # Filter out the rows where outcome is 'SKIPPED'
        filtered_data = self.outcomes[self.outcomes['outcome'] != 'SKIPPED']

        # Calculate the total positions taken
        total_positions = filtered_data.shape[0]

        # Calculate the counts for each outcome type
        profitable_count = filtered_data[filtered_data['outcome'] == 'PROFITABLE'].shape[0]
        unprofitable_count = filtered_data[filtered_data['outcome'] == 'UNPROFITABLE'].shape[0]
        liquidated_count = filtered_data[filtered_data['outcome'] == 'LIQUIDATED'].shape[0]

        percent_profitable = 0
        percent_unprofitable = 0
        percent_liquidated = 0

        if total_positions > 0:
            # Calculate the percentages
            percent_profitable = (profitable_count / total_positions) * 100
            percent_unprofitable = (unprofitable_count / total_positions) * 100
            percent_liquidated = (liquidated_count / total_positions) * 100

        return {
            'total_positions': total_positions,
            'percent_profitable': percent_profitable,
            'percent_unprofitable': percent_unprofitable,
            'percent_liquidated': percent_liquidated
        }



    def get_plot(self):
        # Set up the figure and axis
        fig, ax = plt.subplots(figsize=(14, 7))

        # Plot price and volatility
        ax.plot(self.crypto_data['date'], self.crypto_data['price'], label='Price', color='blue')
        ax2 = ax.twinx()
        ax2.plot(self.crypto_data['date'], self.crypto_data['volatility'], label='Volatility', color='black')

        # Add third axis for fear and greed index
        ax3 = ax.twinx()
        ax3.spines['right'].set_position(("axes", 1.2))  # Offset the right spine of third axis
        ax3.plot(self.crypto_data['date'], self.crypto_data['fear_and_greed'], label='Fear & Greed Index', color='grey')
        ax3.set_ylabel('Fear & Greed Index')

        # Add background color based on outcomes
        colors = {'SKIPPED': 'white', 'PROFITABLE': 'green', 'LIQUIDATED': 'indigo', 'UNPROFITABLE': 'yellow'}
        for outcome, color in colors.items():
            ax.fill_between(self.crypto_data['date'], 0, 1, where=(self.crypto_data['outcome']==outcome),
                            color=color, transform=ax.get_xaxis_transform(), alpha=0.3, label=f'{outcome} Zone')

        # Formatting the plot
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        fig.autofmt_xdate()
        ax.set_title(f'{self.name}: Crypto Price, Volatility, and Fear & Greed Index with Outcome Backgrounds')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax2.set_ylabel('Volatility')

        # Legend
        handles, labels = [], []
        for ax in [ax, ax2, ax3]:
            for handle, label in zip(*ax.get_legend_handles_labels()):
                handles.append(handle)
                labels.append(label)
        plt.legend(handles, labels, loc='upper left')

        return fig, ax


class BackTester:
    def __init__(self, fear_and_greed_path, bitcoin_prices_path, ethereum_prices_path, bitcoin_volatility_path, ethereum_volatility_path):
        # Forwarding the paths received from BackTester to CryptoDataMerger
        self.merger = CryptoDataMerger(
            fear_and_greed_path=fear_and_greed_path,
            bitcoin_prices_path=bitcoin_prices_path,
            ethereum_prices_path=ethereum_prices_path,
            bitcoin_volatility_path=bitcoin_volatility_path,
            ethereum_volatility_path=ethereum_volatility_path
        )
        self.btc, self.eth = self.merger.generate_bitcoin_ethereum_dataframes()

    def backtest(self, name : str, strategy_conditions: Condition, asset: str, start_position : Callable[[DataFrame], bool], start_from : datetime.date | None = None) -> BackTestResult:
        columns = ["start_date", "end_date", "outcome", "open_price", "close_price", "liquidated_at_price"]
        outcome_dataframe = DataFrame(columns=columns)

        crypto_dataframe = self.btc
        if asset.lower() == "eth":
            crypto_dataframe = self.eth

        if start_from:
            crypto_dataframe = crypto_dataframe[crypto_dataframe['date'] >= pd.to_datetime(start_from)]

        sub_frames = get_sub_frames(crypto_dataframe, strategy_conditions.period_days)
        for i, edf in enumerate(sub_frames):
        # for df in sub_frames:
            # Adjusted to pass trimmed dataframe to the callback
            if len(edf) > strategy_conditions.period_days:
                trimmed_edf = edf.iloc[:-strategy_conditions.period_days]
            else:
                trimmed_edf = pd.DataFrame()  # Empty dataframe if not enough rows

            df = edf.iloc[max(0, i - strategy_conditions.period_days + 1):i + 1].copy()
            start_date = df.iloc[0]['date']
            end_date = df.iloc[-1]['date']
            open_price = df.iloc[0]['open']
            close_price = df.iloc[-1]['price']
            outcome, liquidated_at_price = Outcomes.SKIPPED, 0
            if start_position(trimmed_edf):
                strategy_conditions.update_open_price(new_open_price=open_price)
                outcome, liquidated_at_price = self._get_outcome(df, strategy_conditions)

            new_row = {
                "start_date": start_date,
                "end_date": end_date,
                "outcome": outcome.name,
                "open_price": open_price,
                "close_price": close_price,
                "liquidated_at_price": liquidated_at_price
            }
            new_row_df = pd.DataFrame([new_row])
            new_row_df = new_row_df.dropna(axis=1, how='all')
            outcome_dataframe = pd.concat([outcome_dataframe, new_row_df], ignore_index=True)

        return BackTestResult(name, outcome_dataframe, crypto_dataframe)


    def _get_outcome(self, period: DataFrame, condition: Condition) -> Tuple[Outcomes, float]:
        for index, row in period.iterrows():
            low_liquidated = condition.return_current_status(float(row['low'])) == Outcomes.LIQUIDATED
            high_liquidated = condition.return_current_status(float(row['high'])) == Outcomes.LIQUIDATED

            if low_liquidated or high_liquidated:
                return Outcomes.LIQUIDATED, (float(row['low']) if low_liquidated else float(row['high']))

        return condition.return_current_status(period.iloc[-1]['price']), 0
