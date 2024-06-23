import datetime
import pandas as pd
from typing import List

def get_sub_frames(df: pd.DataFrame, period_days: int, start_from : datetime.date | None = None) -> List[pd.DataFrame]:
    sub_frames = []

    for i in range(len(df)):
        # sub_frame = df.iloc[max(0, i - period_days + 1):i + 1].copy()
        sub_frame = df.iloc[:i + 1].copy()
        sub_frames.append(sub_frame)
    return sub_frames
