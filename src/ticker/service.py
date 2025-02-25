import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.ticker.models import UserDefinedTicker
from src.ticker.schemas import UserDefinedTickerCreate


def get_by_user(*, session: Session, ticker_code: str, user_id: uuid.UUID) -> UserDefinedTicker | None:
    return session.execute(
        select(UserDefinedTicker).filter(
            UserDefinedTicker.user_id == user_id,
            UserDefinedTicker.ticker_code == ticker_code
        )
    ).scalar_one_or_none()


def create(*, session: Session, user_id: uuid.UUID, ticker_data: UserDefinedTickerCreate) -> UserDefinedTicker:
    new_ticker = UserDefinedTicker(
        user_id=user_id,
        ticker_code=ticker_data.ticker_code,
        name=ticker_data.name,
        description=ticker_data.description,
        sector=ticker_data.sector,
        drift=ticker_data.drift,
        volatility=ticker_data.volatility,
        jump_intensity=ticker_data.jump_intensity,
        jump_mean=ticker_data.jump_mean,
        jump_std_dev=ticker_data.jump_std_dev,
    )
    session.add(new_ticker)
    session.commit()
    session.refresh(new_ticker)
    return new_ticker


def get_all_by_user(*, session: Session, user_id: uuid.UUID) -> List[UserDefinedTicker]:
    return session.query(UserDefinedTicker).filter(UserDefinedTicker.user_id == user_id).all()
