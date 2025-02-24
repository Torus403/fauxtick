from typing import Dict

from src.ticker.schemas import BuiltInTickerContext, TickerDetails, TickerTypeEnum
from src.ticker.utils import parse_market


BUILT_IN_TICKERS: Dict[str, BuiltInTickerContext] = {
    "A": BuiltInTickerContext(
        name="Titan Industries",
        description="A multinational conglomerate with over 150 years of market dominance in infrastructure and consumer goods, renowned for its AAA credit rating and global supply chain resilience.",
        sector="Technology & Industrial Goods",
        drift_range=(5.0, 8.0),
        volatility_range=(10.0, 20.0),
        jump_intensity_range=(0.5, 1.0),
        jump_mean_range=(-1.0, 2.0),
        jump_std_dev_range=(1.0, 3.0),
    ),
    "B": BuiltInTickerContext(
        name="Solaris Dynamics",
        description="Pioneer in next-generation photovoltaic systems and AI-driven energy optimization platforms, achieving 300% YoY revenue growth in emerging markets.",
        sector="Renewable Energy Technology",
        drift_range=(10.0, 15.0),
        volatility_range=(30.0, 50.0),
        jump_intensity_range=(1.0, 2.0),
        jump_mean_range=(3.0, 5.0),
        jump_std_dev_range=(5.0, 10.0),
    ),
    "C": BuiltInTickerContext(
        name="Ironclad Manufacturing",
        description="Undervalued heavy machinery producer trading at 0.8x book value, maintaining consistent 18% ROIC despite cyclical industry pressures.",
        sector="Industrial Machinery",
        drift_range=(6.0, 9.0),
        volatility_range=(15.0, 25.0),
        jump_intensity_range=(0.5, 1.0),
        jump_mean_range=(-1.0, 2.0),
        jump_std_dev_range=(2.0, 4.0),
    ),
    "D": BuiltInTickerContext(
        name="NexaBio Solutions",
        description="$850M market cap biotech firm developing CRISPR-based neurodegenerative therapies, recently received FDA breakthrough designation for Alzheimer's treatment.",
        sector="Biotechnology",
        drift_range=(12.0, 20.0),
        volatility_range=(40.0, 60.0),
        jump_intensity_range=(2.0, 4.0),
        jump_mean_range=(5.0, 10.0),
        jump_std_dev_range=(10.0, 15.0),
    ),
    "E": BuiltInTickerContext(
        name="Heritage Utilities Co.",
        description="Regulated gas/electric provider with 87 consecutive quarterly dividends and 4.7% yield, serving 2.4 million customers across the Midwest.",
        sector="Utilities",
        drift_range=(4.0, 7.0),
        volatility_range=(10.0, 20.0),
        jump_intensity_range=(0.5, 1.5),
        jump_mean_range=(-2.0, 2.0),
        jump_std_dev_range=(2.0, 4.0),
    ),
    "F": BuiltInTickerContext(
        name="Summit Leisure Group",
        description="Luxury resort operator and cruise line company demonstrating 140% EBITDA volatility relative to GDP fluctuations, currently expanding Asian market footprint.",
        sector="Hospitality & Tourism",
        drift_range=(-2.0, 10.0),
        volatility_range=(20.0, 40.0),
        jump_intensity_range=(1.0, 2.0),
        jump_mean_range=(-1.0, 3.0),
        jump_std_dev_range=(3.0, 6.0),
    ),
}


def get_built_in_category_context(category_key: str) -> BuiltInTickerContext | None:
    return BUILT_IN_TICKERS.get(category_key, None)


def interpolate(letter: str, lower: float, upper: float) -> float:
    """Interpolate a value between lower and upper based on the letter A-Z."""
    ratio = (ord(letter) - ord('A')) / (ord('Z') - ord('A'))
    return lower + ratio * (upper - lower)


def compute_built_in_ticker_derived_details(ticker_code: str, category_context: BuiltInTickerContext) -> TickerDetails:
    """Adds the statistical params, market and ticker type information."""
    # 2nd letter => drift & volatility
    stat_letter = ticker_code[1]
    # turning tuples into arguments (https://stackoverflow.com/questions/1993727/expanding-tuples-into-arguments)
    drift = round(interpolate(stat_letter, *category_context.drift_range), 2)
    volatility = round(interpolate(stat_letter, *category_context.volatility_range), 2)

    # 3rd letter => jump parameters
    jump_letter = ticker_code[2]
    jump_intensity = round(interpolate(jump_letter, *category_context.jump_intensity_range), 2)
    jump_mean = round(interpolate(jump_letter, *category_context.jump_mean_range), 2)
    jump_std_dev = round(interpolate(jump_letter, *category_context.jump_std_dev_range), 2)

    # 4th letter => market
    market_letter = ticker_code[3]
    market = parse_market(market_letter)

    return TickerDetails(
        ticker_code=ticker_code,
        name=category_context.name,
        description=category_context.description,
        sector=category_context.sector,
        drift=drift,
        volatility=volatility,
        jump_intensity=jump_intensity,
        jump_mean=jump_mean,
        jump_std_dev=jump_std_dev,
        market=market,
        type=TickerTypeEnum.BUILT_IN,
    )
