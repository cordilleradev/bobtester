from enum import Enum

class Outcomes(Enum):
    PROFITABLE = "Profitable"
    UNPROFITABLE = "Unprofitable"
    LIQUIDATED = "Liquidated"
    SKIPPED = "Skipped"

class StrategyTypes(Enum):
    LONG_CONDOR = "Long Condor"
    BULL_PUT_SPREAD = "Bull Put Spread"
    BEAR_CALL_SPREAD = "Bear Call Spread"
