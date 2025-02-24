from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.database import Base


class UserDefinedTicker(Base):
    __tablename__ = "user_defined_tickers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ticker_code = Column(String(4), unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    drift = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    jump_intensity = Column(Float, nullable=False)
    jump_mean = Column(Float, nullable=False)
    jump_std_dev = Column(Float, nullable=False)

    # Relationships
    user = relationship("User", back_populates="tickers")
