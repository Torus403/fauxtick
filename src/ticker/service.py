import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.ticker.models import UserDefinedTicker


def get_by_user(*, session: Session, ticker_code: str, user_id: uuid.UUID) -> UserDefinedTicker | None:
    return session.execute(
        select(UserDefinedTicker).filter(
            UserDefinedTicker.user_id == user_id,
            UserDefinedTicker.ticker_code == ticker_code
        )
    ).scalar_one_or_none()

