import pandas as pd
from typing import Tuple

class CryptoDataMerger:
    """
    A class to merge and preprocess cryptocurrency data from various sources.

    Attributes:
        fear_and_greed_path (str): Path to the fear and greed index CSV file.
        bitcoin_prices_path (str): Path to the Bitcoin prices CSV file.
        ethereum_prices_path (str): Path to the Ethereum prices CSV file.
        bitcoin_volatility_path (str): Path to the Bitcoin volatility CSV file.
        ethereum_volatility_path (str): Path to the Ethereum volatility CSV file.
    """

    def __init__(self,
        fear_and_greed_path,
        bitcoin_prices_path,
        ethereum_prices_path,
        bitcoin_volatility_path,
        ethereum_volatility_path,
    ):
        self.fear_and_greed_path = fear_and_greed_path
        self.bitcoin_prices_path = bitcoin_prices_path
        self.ethereum_prices_path = ethereum_prices_path
        self.bitcoin_volatility_path = bitcoin_volatility_path
        self.ethereum_volatility_path = ethereum_volatility_path

    def generate_bitcoin_ethereum_dataframes(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate merged DataFrames for Bitcoin and Ethereum data.

        This method loads data from CSV files, standardizes date columns, converts
        relevant columns to numeric types, merges the data into two DataFrames (one for Bitcoin
        and one for Ethereum), and interpolates missing data.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two DataFrames:
                - Bitcoin merged DataFrame
                - Ethereum merged DataFrame
        """
        # Load data
        fear_and_greed_df = pd.read_csv(self.fear_and_greed_path)
        bitcoin_prices_df = pd.read_csv(self.bitcoin_prices_path)
        ethereum_prices_df = pd.read_csv(self.ethereum_prices_path)
        bitcoin_volatility_df = pd.read_csv(self.bitcoin_volatility_path)
        ethereum_volatility_df = pd.read_csv(self.ethereum_volatility_path)

        # Standardize date columns
        dfs = [fear_and_greed_df, bitcoin_prices_df, ethereum_prices_df, bitcoin_volatility_df, ethereum_volatility_df]
        for df in dfs:
            df.columns = [col.strip().lower().replace(" ", "_").replace("®", "").replace('"', '') for col in df.columns]
            df['date'] = pd.to_datetime(df['date'])

        # Convert columns to numeric, handling special formats
        def convert_to_numeric(df):
            for col in df.columns:
                if df[col].dtype == 'object' and col != 'date':
                    df[col] = df[col].str.replace(',', '').replace('%', '', regex=True).astype(float) / 100
            return df

        dfs = list(map(convert_to_numeric, dfs))
        fear_and_greed_df, bitcoin_prices_df, ethereum_prices_df, bitcoin_volatility_df, ethereum_volatility_df = dfs
        bitcoin_merged_df = pd.merge(fear_and_greed_df, bitcoin_prices_df, on='date', how='inner')
        bitcoin_merged_df = pd.merge(bitcoin_merged_df, bitcoin_volatility_df, on='date', how='inner')
        ethereum_merged_df = pd.merge(fear_and_greed_df, ethereum_prices_df, on='date', how='inner')
        ethereum_merged_df = pd.merge(ethereum_merged_df, ethereum_volatility_df, on='date', how='inner')

        # Clean and interpolate missing data
        bitcoin_merged_df = bitcoin_merged_df.interpolate(method='linear')
        ethereum_merged_df = ethereum_merged_df.interpolate(method='linear')

        return bitcoin_merged_df, ethereum_merged_df
