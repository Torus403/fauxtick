from src.ticker.schemas import TickerDetails, TickerTypeEnum
from src.ticker.models import UserDefinedTicker


def parse_market(market_letter: str) -> str:
    if market_letter == "A":
        return "NYSE"
    elif market_letter == "B":
        return "LSE"
    elif market_letter == "C":
        return "continuous"
    return "unknown"


def compute_user_defined_ticker_derived_details(ticker_code: str, custom_ticker_details: UserDefinedTicker) -> TickerDetails:
    """Adds the market and ticker type information."""
    market_letter = ticker_code[3]
    market = parse_market(market_letter)

    return TickerDetails(
        ticker_code=ticker_code,
        name=custom_ticker_details.name,
        description=custom_ticker_details.description,
        sector=custom_ticker_details.sector,
        drift=custom_ticker_details.drift,
        volatility=custom_ticker_details.volatility,
        jump_intensity=custom_ticker_details.jump_intensity,
        jump_mean=custom_ticker_details.jump_mean,
        jump_std_dev=custom_ticker_details.jump_std_dev,
        market=market,
        type=TickerTypeEnum.USER_DEFINED,
    )
