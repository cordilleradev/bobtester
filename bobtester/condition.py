from bobtester import StrategyTypes, Outcomes

class Bound:
    """
    Represents a range bound which can be inclusive or exclusive.

    Attributes:
        lower (float | None): The lower boundary of the range.
        upper (float | None): The upper boundary of the range.
        inside (bool): Determines if the range is inclusive (True) or exclusive (False).
    """

    def __init__(self, lower: float | None = None, upper: float | None = None, inside: bool = True) -> None:
        """
        Initializes a new Bound instance.

        Args:
            lower (float | None): The lower boundary of the range.
            upper (float | None): The upper boundary of the range.
            inside (bool): Specifies if the boundaries are inclusive (True) or exclusive (False).
        """
        self.lower = lower
        self.upper = upper
        self.inside = inside

    def contains(self, value: float) -> bool:
        """
        Determines if a given value is contained within the bound.

        Args:
            value (float): The value to check.

        Returns:
            bool: True if the value is within the bound, False otherwise.
        """
        if self.inside:
            if self.lower is not None and self.upper is not None:
                return self.lower <= value <= self.upper
            elif self.lower is not None:
                return self.lower <= value
            elif self.upper is not None:
                return value <= self.upper
        else:
            if self.lower is not None and self.upper is not None:
                return value < self.lower or value > self.upper
            elif self.lower is not None:
                return value < self.lower
            elif self.upper is not None:
                return value > self.upper
        return False

    def __str__(self) -> str:
        """
        String representation of the Bound instance.

        Returns:
            str: Descriptive text about the Bound instance.
        """
        return f"Bound(lower={self.lower}, upper={self.upper}, inside={self.inside})"


class Condition:
    """
    Manages trading conditions based on price bounds and specified strategy.

    Attributes:
        open_price (float): The opening price of the trade.
        period_days (int): The number of days the condition is considered.
        profit_below_price_factor (float | None): Factor to calculate the lower profit bound.
        profit_above_price_factor (float | None): Factor to calculate the upper profit bound.
        liquidate_below_price_factor (float | None): Factor to calculate the lower liquidation bound.
        liquidate_above_price_factor (float | None): Factor to calculate the upper liquidation bound.
    """

    def __init__(
        self,
        open_price,
        period_days,
        profit_below_price_factor: float | None = None,
        profit_above_price_factor: float | None = None,
        liquidate_below_price_factor: float | None = None,
        liquidate_above_price_factor: float | None = None,
    ):
        """
        Initializes a new Condition instance.

        Args:
            open_price (float): The opening price of the trade.
            period_days (int): The duration in days for the trading condition.
            profit_below_price_factor (float | None): Multiplier to set the lower profit threshold.
            profit_above_price_factor (float | None): Multiplier to set the upper profit threshold.
            liquidate_below_price_factor (float | None): Multiplier to set the lower liquidation threshold.
            liquidate_above_price_factor (float | None): Multiplier to set the upper liquidation threshold.
        """
        self.open_price = open_price
        self.profit_below_price_factor = profit_below_price_factor
        self.profit_above_price_factor = profit_above_price_factor
        self.liquidate_below_price_factor = liquidate_below_price_factor
        self.liquidate_above_price_factor = liquidate_above_price_factor
        self.period_days = period_days
        # Initialize bounds and strategy based on the provided factors
        self.initialize_bounds()
        self.determine_strategy()

    def initialize_bounds(self):
        """Initializes the profit and liquidation bounds based on the provided price factors."""
        self.profit_bound = Bound(
            lower=self.open_price * (1 - self.profit_below_price_factor) if self.profit_below_price_factor is not None else None,
            upper=self.open_price * (1 + self.profit_above_price_factor) if self.profit_above_price_factor is not None else None,
        )

        self.liquidate_bound = Bound(
            lower=self.open_price * (1 - self.liquidate_below_price_factor) if self.liquidate_below_price_factor is not None else None,
            upper=self.open_price * (1 + self.liquidate_above_price_factor) if self.liquidate_above_price_factor is not None else None,
            inside=False
        )

    def determine_strategy(self):
        """Determines the trading strategy based on the set profit bounds."""
        if self.profit_bound.upper and self.profit_bound.lower:
            self.strategy = StrategyTypes.LONG_CONDOR
        elif self.profit_bound.upper and not self.profit_bound.lower:
            self.strategy = StrategyTypes.BULL_PUT_SPREAD
        elif self.profit_bound.lower and not self.profit_bound.upper:
            self.strategy = StrategyTypes.BEAR_CALL_SPREAD

    def update_open_price(self, new_open_price: float) -> None:
        """Updates the open price and reinitializes conditions based on the new price."""
        self.__init__(
            new_open_price,
            self.period_days,
            self.profit_below_price_factor,
            self.profit_above_price_factor,
            self.liquidate_below_price_factor,
            self.liquidate_above_price_factor,
        )

    def __str__(self) -> str:
        """
        String representation of the Condition instance.

        Returns:
            str: Descriptive text about the trading conditions and strategy.
        """
        return (
            f"Conditions(\n"
            f"    profit_bound={self.profit_bound},\n"
            f"    liquidate_bound={self.liquidate_bound},\n"
            f"    strategy={self.strategy.name}\n"
            f")"
        )

    def return_current_status(self, current_price: float) -> Outcomes:
        """
        Determines the current trading status based on the current price.

        Args:
            current_price (float): The current market price.

        Returns:
            Outcomes: The current trading outcome (e.g., LIQUIDATED, PROFITABLE, UNPROFITABLE).
        """
        if self.liquidate_bound.contains(current_price):
            return Outcomes.LIQUIDATED
        elif self.profit_bound.contains(current_price):
            return Outcomes.PROFITABLE
        else:
            return Outcomes.UNPROFITABLE
