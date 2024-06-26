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
        Generates merged and preprocessed dataframes for Bitcoin and Ethereum.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: Merged and preprocessed dataframes for Bitcoin and Ethereum.
        """
        fear_and_greed_df = pd.read_csv(self.fear_and_greed_path)
        bitcoin_prices_df = pd.read_csv(self.bitcoin_prices_path)
        ethereum_prices_df = pd.read_csv(self.ethereum_prices_path)
        bitcoin_volatility_df = pd.read_csv(self.bitcoin_volatility_path, delimiter=';')
        ethereum_volatility_df = pd.read_csv(self.ethereum_volatility_path, delimiter=';')

        for df in [
            fear_and_greed_df,
            bitcoin_prices_df,
            ethereum_prices_df,
            bitcoin_volatility_df,
            ethereum_volatility_df
        ]:
            df.columns = [col.strip().lower().replace(" ", "_").replace("®", "").replace('"', '') for col in df.columns]
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            else:
                raise ValueError("Each dataframe must have a 'date' column")

        def convert_to_numeric(df):
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace(',', '')
                    if df[col].str.contains('%').any():
                        df[col] = df[col].str.rstrip('%').astype(float) / 100
                    else:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
            return df

        fear_and_greed_df = convert_to_numeric(fear_and_greed_df)
        bitcoin_prices_df = convert_to_numeric(bitcoin_prices_df)
        ethereum_prices_df = convert_to_numeric(ethereum_prices_df)
        bitcoin_volatility_df = convert_to_numeric(bitcoin_volatility_df)
        ethereum_volatility_df = convert_to_numeric(ethereum_volatility_df)

        bitcoin_merged_df = pd.merge(fear_and_greed_df, bitcoin_prices_df, on='date', how='outer')
        bitcoin_merged_df = pd.merge(bitcoin_merged_df, bitcoin_volatility_df, on='date', how='outer')
        ethereum_merged_df = pd.merge(fear_and_greed_df, ethereum_prices_df, on='date', how='outer')
        ethereum_merged_df = pd.merge(ethereum_merged_df, ethereum_volatility_df, on='date', how='outer')

        bitcoin_merged_df = bitcoin_merged_df.sort_values(by='date')
        ethereum_merged_df = ethereum_merged_df.sort_values(by='date')

        bitcoin_merged_df = bitcoin_merged_df.interpolate(method='linear')
        ethereum_merged_df = ethereum_merged_df.interpolate(method='linear')

        for col in ['index', 'price', 'open', 'high', 'low', 'change_%', 'volatility']:
            if col not in bitcoin_merged_df.columns:
                bitcoin_merged_df[col] = pd.NA
            if col not in ethereum_merged_df.columns:
                ethereum_merged_df[col] = pd.NA

        bitcoin_merged_df.drop(columns=['vol.'], inplace=True)
        ethereum_merged_df.drop(columns=['vol.'], inplace=True)

        bitcoin_merged_df.dropna(inplace=True)
        ethereum_merged_df.dropna(inplace=True)

        bitcoin_merged_df['change_%'] = bitcoin_merged_df['change_%'].round(2)
        ethereum_merged_df['change_%'] = ethereum_merged_df['change_%'].round(2)

        bitcoin_merged_df['volatility'] = bitcoin_merged_df['volatility'].round(2)
        ethereum_merged_df['volatility'] = ethereum_merged_df['volatility'].round(2)
        bitcoin_merged_df.rename(columns={'index': 'fear_and_greed'}, inplace=True)
        ethereum_merged_df.rename(columns={'index': 'fear_and_greed'}, inplace=True)

        def calculate_rsi(df, window=14):
            delta = df['price'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=window, min_periods=1).mean()
            avg_loss = loss.rolling(window=window, min_periods=1).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            df['rsi'] = rsi
            return df

        bitcoin_merged_df = calculate_rsi(bitcoin_merged_df)
        ethereum_merged_df = calculate_rsi(ethereum_merged_df)

        return bitcoin_merged_df, ethereum_merged_df