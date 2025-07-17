from typing import TypedDict, Literal, List

class TopMoversArgs(TypedDict):
    period: Literal["1d", "7d", "30d"]
    limit: int            # how many coins to return

class PricePlotArgs(TypedDict):
    coin: str             # coin symbol, e.g. BTC
    days: int             # days back to plot

class ForecastArgs(TypedDict):
    coin: str             # coin name, e.g. bitcoin
    days: int             # days ahead to forecast

# Master registry (could expand later)
ALLOWED_FUNCTIONS: dict[str, type] = {
    "get_top_movers": TopMoversArgs,
    "plot_price": PricePlotArgs,
    "forecast_price": ForecastArgs,
}
