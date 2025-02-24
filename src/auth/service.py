from sqlalchemy import select
from sqlalchemy.orm import Session

from src.security import verify_password
from src.user.models import User
from src.user import service


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = service.get_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
