import datetime
import pandas as pd
from typing import List

def get_sub_frames(df: pd.DataFrame, period_days: int, start_from : datetime.date | None = None) -> List[pd.DataFrame]:
    """
    Splits a DataFrame into a list of sub-DataFrames based on the specified period in days.

        Parameters:
    df (pd.DataFrame): The input DataFrame to be split.
    period_days (int): The number of days for each sub-DataFrame period.
    start_from (datetime.date | None): Optional starting date for the sub-DataFrames. Defaults to None.

        Returns:
    List[pd.DataFrame]: A list of sub-DataFrames, each containing data up to the current day in the loop.
    """
    sub_frames = []

    for i in range(len(df)):
        # sub_frame = df.iloc[max(0, i - period_days + 1):i + 1].copy()
        sub_frame = df.iloc[:i + 1].copy()
        sub_frames.append(sub_frame)
    return sub_frames
