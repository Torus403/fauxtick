from pydantic import BaseModel
from typing import Tuple, Optional
from enum import Enum


class BuiltInTickerContext(BaseModel):
    name: str
    description: str
    sector: str
    drift_range: Tuple[float, float]
    volatility_range: Tuple[float, float]
    jump_intensity_range: Tuple[float, float]
    jump_mean_range: Tuple[float, float]
    jump_std_dev_range: Tuple[float, float]


class TickerTypeEnum(str, Enum):
    BUILT_IN = "BUILT_IN"
    USER_DEFINED = "USER_DEFINED"


class TickerDetails(BaseModel):
    ticker_code: str
    name: str
    description: Optional[str]
    sector: Optional[str]
    drift: float
    volatility: float
    jump_intensity: float
    jump_mean: float
    jump_std_dev: float
    market: str
    type: TickerTypeEnum


class UserDefinedTickerCreate(BaseModel):
    ticker_code: str
    name: str
    description: Optional[str]
    sector: Optional[str]
    drift: float
    volatility: float
    jump_intensity: float
    jump_mean: float
    jump_std_dev: float
