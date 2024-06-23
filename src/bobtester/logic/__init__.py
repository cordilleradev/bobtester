from enum import Enum

class PathsEnum(Enum):
    BITCOIN_PRICES = "./data/bitcoin-prices.csv"
    BITCOIN_VOLATILITY = "./data/bitcoin-volatility.csv"
    ETHEREUM_PRICES = "./data/ethereum-prices.csv"
    ETHEREUM_VOLATILITY = "./data/ethereum-volatility.csv"
    FEAR_AND_GREED_INDEX = "./data/fear-and-greed-index.csv"

class Outcomes(Enum):
    PROFITABLE = "Profitable"
    UNPROFITABLE = "Unprofitable"
    LIQUIDATED = "Liquidated"
    SKIPPED = "Skipped"

class StrategyTypes(Enum):
    LONG_CONDOR = "Long Condor"
    BULL_PUT_SPREAD = "Bull Put Spread"
    BEAR_CALL_SPREAD = "Bear Call Spread"
